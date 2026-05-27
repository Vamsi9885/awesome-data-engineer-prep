# ETL Operations & Incident Management — Interview Q&A

> **Topic:** Production ETL support, incident response, SLA management, and operational scaling  
> **Level:** Senior / Lead Data Engineer  
> **Format:** Scenario-based behavioral + technical questions

---

## Table of Contents

1. [Prioritizing Three Simultaneous Pipeline Failures](#1-prioritizing-three-simultaneous-pipeline-failures)
2. [First Steps Before Deep-Diving Into the Highest-Priority Job](#2-first-steps-before-deep-diving-into-the-highest-priority-job)
3. [Long-Running ETL Job — Kill vs. Let It Continue](#3-long-running-etl-job--kill-vs-let-it-continue)
4. [Database CPU Spike While ETL Is Running](#4-database-cpu-spike-while-etl-is-running)
5. [ETL Job About to Breach SLA](#5-etl-job-about-to-breach-sla)
6. [Communicating a Technical Issue to Non-Technical Stakeholders](#6-communicating-a-technical-issue-to-non-technical-stakeholders)
7. [Supporting a Legacy Tool With No Documentation](#7-supporting-a-legacy-tool-with-no-documentation)
8. [Pattern-Based ETL Failure — Every Wednesday 10 PM](#8-pattern-based-etl-failure--every-wednesday-10-pm)
9. [Global Outage — No ETL Access](#9-global-outage--no-etl-access)
10. [Preventing Temporary Workarounds From Becoming Technical Debt](#10-preventing-temporary-workarounds-from-becoming-technical-debt)
11. [Scaling ETL Operations for Thousands of Jobs](#11-scaling-etl-operations-for-thousands-of-jobs)

---

## 1. Prioritizing Three Simultaneous Pipeline Failures

**Question:**  
Three critical ETL pipelines fail simultaneously:
- Executive dashboard pipeline
- Mid-level report pipeline
- Upstream pipeline feeding 100 downstream jobs

Which one would you prioritize first and why?

---

**Answer:**

**Priority order: Upstream pipeline → Executive dashboard → Mid-level report**

The **upstream pipeline** is the highest priority, even though an executive dashboard feels more urgent at first glance.

Here's the reasoning:

**Why upstream pipeline first:**
- It feeds **100 downstream jobs**. If it stays broken, those 100 jobs either fail, produce stale data, or skip silently — compounding the blast radius with every passing minute.
- Fixing this one pipeline has a **multiplier effect**: once it recovers and emits clean data, many downstream jobs may self-heal on retry without further intervention.
- Delay here causes cascading failures that become exponentially harder to recover from.

**Why executive dashboard second:**
- It has **direct business visibility** — executives or leadership are likely already asking questions.
- The SLA impact is immediate and reputational. Even if the data is delayed, stakeholders need to know ETA.
- It typically pulls from a curated/aggregated layer, so it's scoped and contained — faster to fix.

**Why mid-level report last:**
- It's impactful but usually has a **wider tolerance window** than executive reporting.
- Unless it has downstream dependencies of its own, the blast radius is limited.

**Key principle:**  
> *Always prioritize by blast radius first, then by visibility, then by recovery complexity.*

---

## 2. First Steps Before Deep-Diving Into the Highest-Priority Job

**Question:**  
Before focusing on the highest-priority failed job — do you completely ignore the other failed jobs? What do you do first before deep-diving into one pipeline?

---

**Answer:**

**No — you never fully ignore the other jobs. The first 2–3 minutes are about awareness, not action.**

**Immediate triage protocol (before deep-diving into anything):**

1. **Do a 60-second blast radius check across all three failures**
   - Are all three caused by the same root issue (e.g., network outage, storage unavailability, credential expiry)?
   - If yes → fixing one fix may resolve all three simultaneously. This changes your entire strategy.
   - If no → they need independent remediation; you now sequence correctly.

2. **Page / alert the right owners**
   - If your team has specialists per pipeline or per domain, loop them in now, not after you've spent 30 minutes debugging solo.
   - Assign one person per critical failure so work happens in parallel.

3. **Check for a common upstream dependency**
   - Shared databases, shared landing zones (S3/ADLS), shared Kafka topics, shared credential vaults — a single broken dependency could explain all three failures.

4. **Post an initial incident acknowledgement**
   - Even a 2-line Slack/Teams message: "Three pipelines down, investigating, ETA update in 15 min" buys goodwill and reduces stakeholder noise while you focus.

5. **Only then deep-dive into the highest-priority pipeline**

**The anti-pattern to avoid:**  
> Jumping headfirst into pipeline #1's logs for 45 minutes, only to discover at minute 47 that all three failed because of an expired service account key that takes 2 minutes to rotate.

---

## 3. Long-Running ETL Job — Kill vs. Let It Continue

**Question:**  
A long-running ETL job exceeds its normal runtime. The job normally takes 2 hours; today it's at 2h 45m and still running. When do you decide to kill/restart vs. let it continue?

---

**Answer:**

**You need data before you decide — never kill blindly.**

**Step 1 — Diagnose immediately at the 2h 30m mark (before it's critical):**

Check the following:
- **Progress indicators**: Is the job making forward progress? (rows processed, stages completed, partitions scanned). A job at 90% with 45 min to go is very different from a job stuck at 40%.
- **Execution plan**: In Spark — check the Spark UI for stuck stages, skewed tasks, or a single task holding up the entire job. In ADF — check the activity run details.
- **Resource utilization**: Is the cluster at 100% CPU/memory? Is there a GC storm? Are executors getting evicted?
- **Locks and waits**: If writing to a DB — check for table locks, deadlocks, or I/O contention.
- **Data volume anomaly**: Was today's input data significantly larger than usual? (e.g., a missed run from yesterday also loaded today)

**Decision matrix:**

| Observation | Action |
|---|---|
| Job is making steady progress, no errors, data volume is larger than usual | Let it run with a revised ETA |
| Job is stuck on a single task / stage for > 20 min with no progress | Kill and investigate root cause before restart |
| Resource exhaustion (OOM, disk spill, executor loss) | Kill, right-size the cluster or add partitions, then restart |
| Progress is normal but SLA breach is imminent | Notify stakeholders, decide restart only if restart is faster than completion |
| Stuck with lock contention on DB | Kill, resolve the lock, restart |

**Before killing — ask:**
> "Is restarting actually faster than waiting?" If the job is at 85% completion and restart means re-processing from scratch, waiting wins. If it's at 15% and clearly hung, kill it.

**Post-kill checklist:**
- Confirm idempotency — can the job safely re-run without duplicate records or data corruption?
- Check for partial writes — clean up any incomplete data before restarting.
- Add a monitoring alert for next time so you catch the anomaly at 2h 15m, not 2h 45m.

---

## 4. Database CPU Spike While ETL Is Running

**Question:**  
The underlying database reaches 90% CPU while the ETL job is still running successfully. What immediate actions would you take?

---

**Answer:**

**90% CPU is a warning sign, not yet a failure — but it will become one. Act in layers.**

**Immediate (first 5 minutes):**

1. **Identify the top consuming queries**
   - Run `pg_stat_activity` (Postgres), `sys.dm_exec_requests` (SQL Server), or the equivalent for your DB.
   - Look for long-running queries, full table scans, or runaway aggregations tied to your ETL session.

2. **Check parallelism settings**
   - Is the ETL job running too many parallel connections / threads against the DB?
   - Reduce `maxConnections` or degree of parallelism in the pipeline config to throttle DB pressure immediately.

3. **Check for unintended full table scans**
   - A missing or stale index on a filter column can cause the DB to do full scans at scale.
   - Run `EXPLAIN ANALYZE` on the ETL query to confirm the execution plan.

4. **Kill or deprioritize non-critical concurrent workloads**
   - Are there ad-hoc analyst queries, reports, or other ETL jobs competing for the same DB at the same time?
   - Temporarily suspend them or route them to a read replica.

**Short-term (within the hour):**

- If the DB has **read replicas**, redirect read-heavy ETL queries there immediately.
- Implement **connection pooling** (PgBouncer, HikariCP) if not already in place.
- Review **batch sizes** — if the ETL writes in large uncommitted transactions, reduce batch size to reduce lock duration.
- Trigger a **manual VACUUM / ANALYZE** (Postgres) or **UPDATE STATISTICS** if table bloat or stale stats are causing poor query plans.

**Communication:**
- Notify the DBA team immediately — even if the job is running "successfully" now, sustained 90% CPU risks query timeouts, connection exhaustion, or a full DB outage.

---

## 5. ETL Job About to Breach SLA

**Question:**  
Only 10 minutes left before an SLA miss. What accountability steps do you take?

---

**Answer:**

**At T-10 minutes, you are past the "fix it silently" window. Accountability takes over.**

**Immediate actions:**

1. **Notify stakeholders proactively — before the SLA is missed**
   - Send a brief, factual message to the stakeholder group and your manager:
     > "Pipeline X is currently running and projected to miss the [time] SLA by approximately [N] minutes. Root cause is under investigation. Next update in 10 minutes."
   - Proactive communication is always received better than a missed SLA with no warning.

2. **Declare the SLA breach formally if you cannot recover**
   - Update your incident tracking tool (Jira, ServiceNow, PagerDuty, etc.) with the breach timestamp and reason.
   - This creates an auditable record.

3. **Communicate business impact clearly**
   - Who is affected? What decisions or reports depend on this data?
   - Can downstream consumers work with slightly stale data temporarily?
   - Is there a manual workaround (e.g., yesterday's data refresh) that buys time?

4. **Attempt a fast-path recovery if applicable**
   - Can you skip a non-critical transformation and deliver a partial dataset within SLA?
   - Can you trigger a lightweight fallback query to populate the dashboard with stale-but-labeled data?

**Post-breach (within 24 hours):**

- Write an **incident report / RCA (Root Cause Analysis)**:
  - What failed
  - Why it failed
  - What the impact was
  - What will prevent recurrence (monitoring, alert tuning, pipeline optimization)
- Share it with stakeholders and leadership — transparency builds trust even after failures.

**Key principle:**  
> *SLA misses happen. How you communicate and own them determines your credibility far more than the miss itself.*

---

## 6. Communicating a Technical Issue to Non-Technical Stakeholders

**Question:**  
A non-technical stakeholder joins the incident bridge. How do you explain a complex technical issue to them?

---

**Answer:**

**Switch to impact language, not technical language — immediately.**

**Framework: WHAT → WHY (simple) → WHEN → WHAT NEXT**

| Technical language (avoid) | Stakeholder language (use) |
|---|---|
| "The Spark job hit an OOM on the executor nodes" | "The data processing system ran out of memory handling today's larger-than-usual data volume" |
| "The upstream Kafka topic lag is 4 hours behind" | "Data from our source systems is arriving 4 hours late, which delays everything downstream" |
| "ADF pipeline failed at the copy activity due to a 403 on ADLS" | "A permissions issue is preventing the pipeline from accessing the data storage layer" |

**Practical steps on the bridge call:**

1. **Acknowledge their presence immediately** — "Thanks for joining. Let me give you a quick business-level summary."

2. **Lead with business impact, not root cause:**
   > "The executive dashboard is currently showing data from yesterday morning. We expect to have today's data available by [ETA]. No data has been lost — it's a delay, not a loss."

3. **Give a clear ETA and confidence level:**
   > "We're 70% confident we can restore by 3 PM. If that changes, you'll hear from me first."

4. **Offer one specific action they can take** if decisions can't wait:
   > "If you need to present before 3 PM, I can pull a manual snapshot of yesterday's numbers for you right now."

5. **Don't explain the fix in technical detail** — say "the engineering team is actively working on it" and redirect energy to resolution.

6. **Assign a communication owner** — one person on the incident bridge should be dedicated to stakeholder updates so the rest of the team can focus on fixing.

---

## 7. Supporting a Legacy Tool With No Documentation

**Question:**  
You've joined a new team. There's an old, unsupported tool with no documentation and no SMEs available. How do you start supporting it?

---

**Answer:**

**Treat it like an archaeological dig — systematic, patient, and evidence-based.**

**Phase 1 — Understand what it does (Week 1)**

1. **Read the codebase / configs top-down**
   - Start with entry points: main scripts, config files, cron jobs, scheduler definitions.
   - Identify: what data comes in, what transformations happen, what goes out, and where.

2. **Map all external dependencies**
   - What databases does it connect to?
   - What file paths / buckets / APIs does it read from or write to?
   - What credentials or service accounts does it use?

3. **Observe it running in production**
   - Watch a few successful runs end-to-end. Take notes on timing, file sizes, DB interactions.
   - Capture a baseline: typical runtime, typical row counts, output file sizes.

4. **Mine version control history**
   - Git log is often the only documentation legacy tools have.
   - Read commit messages, PR descriptions, and blame history to understand the "why" behind decisions.

**Phase 2 — Stabilize it (Week 2–3)**

5. **Identify failure modes**
   - Look at historical logs, on-call tickets, and any monitoring alerts for the tool.
   - Catalog: what breaks, how often, and what the manual remediation has been.

6. **Add basic observability if it doesn't exist**
   - Wrap it with logging: job start, row counts, duration, success/failure.
   - Add email/Slack alerts on failure. Even a simple shell wrapper with `mail` on non-zero exit codes is better than nothing.

7. **Document as you go**
   - Every discovery goes into a living runbook: what the tool does, how to run it manually, known failure modes, and their fixes.
   - This runbook becomes the documentation that didn't exist.

**Phase 3 — Reduce risk (Month 1+)**

8. **Build a test harness**
   - Create a staging environment where you can run the tool safely against synthetic or copied data.
   - This lets you make changes without fear.

9. **Plan for modernization or decommission**
   - If the tool is truly unsupportable long-term, start the conversation early about migrating to a supported alternative.
   - Quantify the operational risk: "This tool has no tests, no docs, and no escalation path. Here is what it would take to replace it."

---

## 8. Pattern-Based ETL Failure — Every Wednesday 10 PM

**Question:**  
A job runs at 10 AM and 10 PM daily. Every Wednesday 10 PM run fails initially but succeeds after retries. How would you investigate the anomaly?

---

**Answer:**

**This is a pattern, not random noise — patterns have causes. Your job is to narrow the hypothesis space.**

**Step 1 — Confirm and characterize the pattern**

- Pull at least 4–6 weeks of run history for this job.
- Confirm: Does it *always* fail on Wednesday 10 PM, or occasionally other times too?
- How many retries does it typically need before succeeding? Is that number increasing over time?
- What is the failure error? Is it always the same error, or does it vary?

**Step 2 — What is special about Wednesday 10 PM?**

Think about what batch processes, scheduled jobs, or business events happen on Wednesdays:

| Hypothesis | What to check |
|---|---|
| Competing workload on Wednesday nights | Check if any weekly batch jobs, reports, backups, or maintenance tasks run Wednesday nights and contend for DB/CPU/storage |
| End-of-week data volume spike | Is Wednesday's input data volume consistently larger? (e.g., weekly aggregations, mid-week cutoffs) |
| DB maintenance window | Some DBs run auto-VACUUM, index rebuilds, or stats updates on a weekly schedule — check your DBA team |
| Upstream data delivery timing | Does a source system deliver data on a different cadence that causes the Wednesday 10 PM load to be heavier or delayed? |
| Network/cloud resource contention | Some cloud providers have higher usage patterns mid-week evenings; check cloud metrics |
| Lock contention | Is another Wednesday-evening job holding a lock on a table this pipeline reads or writes? |

**Step 3 — Instrument more deeply**

- Add timing logs to each phase of the job (extract, transform, load) to see *which phase* fails on Wednesday nights.
- Capture the exact error message and stack trace on the next occurrence — don't just retry silently.
- Add a metric: time-to-first-retry and number-of-retries, so you can track whether it's getting worse.

**Step 4 — Hypothesis testing**

- If the hypothesis is "competing workload": check with the team if a weekly batch job can be rescheduled to 11 PM or midnight.
- If the hypothesis is "data volume": pre-scale the cluster/resource allocation for Wednesday's 10 PM run specifically.
- If the hypothesis is "DB maintenance": coordinate with DBA to shift the maintenance window or add a retry buffer.

**Step 5 — Fix and validate**

- Implement the fix for the most likely hypothesis.
- Monitor for at least 3 consecutive Wednesdays before closing the issue.
- Document the finding in the runbook: "Wednesday 10 PM failures were caused by X. Fixed by Y. Monitor if recurrence observed."

**Key insight:**  
> *Retrying successfully does not mean the problem is solved — it means the problem is hidden. Retries buy time; root cause analysis buys stability.*

---

## 9. Global Outage — No ETL Access

**Question:**  
Nobody can log into ETL servers. The entire ecosystem is inaccessible. What is the immediate on-bridge protocol?

---

**Answer:**

**When you can't access anything, the protocol shifts from technical diagnosis to incident command.**

**First 5 minutes — Establish scope and command:**

1. **Confirm the blast radius immediately**
   - Is it just ETL servers, or is the entire infrastructure affected? (network, VPN, cloud tenant, data center)
   - Can other teams (application teams, DBAs, cloud ops) access their systems, or is this company-wide?
   - This determines whether it's a data team problem or an infrastructure/cloud provider problem.

2. **Assign an Incident Commander (IC)**
   - One person owns the bridge: drives the agenda, tracks actions, and communicates externally.
   - Everyone else focuses on their specific area. No overlapping roles.

3. **Open the official incident channel**
   - Create a dedicated Slack/Teams channel or bridge line for this incident immediately.
   - All updates, findings, and decisions go there — not in private DMs.

**First 15 minutes — Parallel investigation tracks:**

| Track | Owner | Actions |
|---|---|---|
| Network / VPN | Infrastructure / Cloud Ops | Check VPN connectivity, firewall rules, cloud network ACLs |
| Cloud provider status | On-call engineer | Check AWS/Azure/GCP status page for active incidents in your region |
| Authentication / Identity | IAM / Security team | Check if SSO, Active Directory, or identity provider is down |
| ETL servers directly | Systems team | Attempt console access (not SSH) — is the OS up? |

4. **Check cloud provider status pages first**
   - For Azure: status.azure.com
   - For AWS: health.aws.amazon.com
   - For GCP: status.cloud.google.com
   - If the provider is having an incident in your region, you are in "wait and watch" mode, not "fix" mode.

5. **Escalate to senior leadership and stakeholders**
   - A global outage affecting all ETL = business-critical. Leadership needs to know within 10 minutes.
   - Be factual: "We cannot access any ETL systems. This is being treated as P1. We are investigating cause. Next update in 20 minutes."

**While waiting for access to be restored:**

- Prepare a **runbook of everything that will need to be restarted** once access returns.
- Identify which jobs have SLAs that will be breached and in what order they need to be recovered.
- Draft stakeholder communications for different recovery scenarios (restored in 1 hour vs. 4 hours vs. 8+ hours).

**Post-restoration:**

- Do not restart all jobs simultaneously — prioritize by SLA and blast radius.
- Validate data integrity before marking jobs as recovered.
- Conduct a full post-mortem within 24–48 hours.

---

## 10. Preventing Temporary Workarounds From Becoming Technical Debt

**Question:**  
A recurring issue has been handled through a workaround for a long time. How do you prevent temporary fixes from becoming permanent technical debt?

---

**Answer:**

**The workaround becomes debt the moment it loses its "temporary" label in people's minds. The fix is process, not willpower.**

**In the moment — when applying the workaround:**

1. **Create a ticket immediately, not later**
   - The moment you apply a workaround, open a JIRA/GitHub issue titled clearly: *"[WORKAROUND ACTIVE] Permanent fix for X"*
   - Document: what the workaround is, why it was applied, what risks it carries, and what the permanent fix looks like.
   - Link the ticket to the runbook, the monitoring alert, and the incident record.

2. **Set an expiry or review date on the workaround**
   - Add a code comment with a deadline: `# TEMP WORKAROUND - ticket #1234 - review by [date]`
   - Add it to the sprint board for the next cycle with an explicit acceptance criterion.

3. **Communicate the workaround to the team**
   - "We have a workaround in place for X. It works but has these known risks. The permanent fix is in the backlog."
   - If everyone knows, no one assumes it's the intended state.

**In the medium term — keeping it visible:**

4. **Make workarounds part of sprint planning**
   - Maintain a "tech debt / workarounds" backlog section.
   - During each sprint planning, explicitly review the oldest open workaround tickets.
   - If it keeps getting deprioritized, escalate: "This workaround has been active for 3 months. Here is the operational risk."

5. **Quantify the cost of the workaround**
   - How many engineer-hours per month does it consume in manual intervention?
   - What is the risk if it fails silently?
   - A workaround that costs 4 hours/month for 12 months = 48 hours of engineering time. That's the ROI argument for fixing it properly.

6. **Make the workaround painful to maintain**
   - Add monitoring and alerting specifically for the workaround path — every time it triggers, it creates noise that keeps it visible.
   - Do not make the workaround "too comfortable" or it will never get replaced.

**Key principle:**  
> *A workaround with a ticket and an owner is a known liability. A workaround without a ticket is invisible debt that will eventually create an incident.*

---

## 11. Scaling ETL Operations for Thousands of Jobs

**Question:**  
Manual monitoring is no longer feasible as the number of ETL jobs grows to thousands. What strategies and automations would you implement to make operations manageable at scale?

---

**Answer:**

**At thousands of jobs, manual monitoring is not just inefficient — it's a liability. The goal is to shift from reactive firefighting to proactive, automated operations.**

### A. Observability & Monitoring

**1. Centralized metadata store**
- Maintain a pipeline catalog: job name, owner, schedule, SLA, dependencies, criticality tier (P1/P2/P3).
- Every job registers itself in the catalog on creation (GitOps-driven or API-driven).

**2. Standardized metrics for every job**
- Every ETL job emits: start time, end time, rows read, rows written, rows rejected, status, duration.
- Publish these to a central metrics store (Prometheus + Grafana, Datadog, Azure Monitor, or a custom BigQuery/Delta Lake metrics table).

**3. SLA-aware alerting**
- Alert based on SLA breach risk, not just failure: "Job X has 20 minutes left before SLA and is only 30% complete."
- Separate alert severity by business criticality — P1 jobs page on-call immediately; P3 jobs create a ticket.

**4. Anomaly detection on job runtimes**
- Build a baseline of expected runtime per job (rolling 30-day average ± N standard deviations).
- Alert when a job runs significantly longer or shorter than baseline — both are signals of problems.

### B. Automation

**5. Automated retries with smart backoff**
- Configure retry policies per job tier: P1 jobs retry aggressively (3x, 2-minute intervals); P3 jobs retry once with a 30-minute backoff.
- Log every retry with reason so patterns surface in dashboards.

**6. Self-healing pipelines**
- For known transient failures (e.g., connection timeouts, temporary resource unavailability), implement auto-remediation scripts that restart the job, rotate credentials, or scale up resources automatically.

**7. Data quality gates**
- Embed automated data quality checks (row count validation, null rate checks, schema drift detection) as a post-load step.
- Fail loudly and early if data quality degrades — don't let bad data propagate silently.

**8. Dependency-aware scheduling**
- Use an orchestrator (Apache Airflow, Azure Data Factory with dependencies, Prefect, Dagster) that understands upstream/downstream relationships.
- If an upstream job fails, automatically pause dependent downstream jobs rather than letting them run on stale data.

### C. Operational Practices

**9. Tiered SLA management**
- Classify all jobs: Tier 1 (business-critical, hard SLA), Tier 2 (important, soft SLA), Tier 3 (best-effort).
- Dedicate on-call energy to Tier 1 only. Tier 2 and 3 alerts go to a queue.

**10. GitOps-driven pipeline management**
- All pipeline configs, schedules, and SLA definitions live in Git.
- Any change to a pipeline goes through PR review and CI/CD — this prevents configuration drift and creates audit trails.

**11. Runbook automation**
- For every recurring failure pattern, write a runbook.
- Then automate the runbook: if error pattern X is detected, execute remediation script Y automatically, and only page a human if Y fails.

**12. Capacity and cost monitoring**
- At thousands of jobs, compute cost becomes significant. Track spend per pipeline, per team, per domain.
- Identify and terminate idle or zombie jobs consuming cluster resources without producing value.

### D. Team Process

**13. On-call rotation with clear scope**
- Define exactly which jobs are on-call responsibilities and which are handled during business hours.
- Avoid "everyone owns everything" — at scale, it means no one owns anything.

**14. Regular pipeline health reviews**
- Weekly or biweekly review: slowest jobs, most-failing jobs, jobs with the most manual intervention.
- Use data to drive prioritization of tech debt paydown.

**Summary table:**

| Problem at scale | Solution |
|---|---|
| Too many alerts, alert fatigue | Tiered alerting + SLA-based smart alerts |
| Manual retry effort | Automated retry with smart backoff |
| Unknown SLA owners | Centralized pipeline catalog with owners |
| Configuration drift | GitOps for all pipeline configs |
| Silent data quality failures | Automated DQ gates post-load |
| Runaway compute costs | Per-pipeline cost tracking + zombie job detection |
| On-call overload | Tier-based escalation + runbook automation |

---

*Last updated: May 2026*  
*Author: Vamsi — Senior Data Engineer*  
*Tags: `etl` `incident-management` `data-engineering` `interview-prep` `sla` `operations`*