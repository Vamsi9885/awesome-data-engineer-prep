# 🎛️ Pipeline Orchestration in Production (ADF, Airflow, Step Functions, Composer)

## 1. Concept Explanation

**Orchestration** is the control plane of data engineering: scheduling, dependencies, retries, SLAs, environment promotion, and operational governance.

Without orchestration, data jobs become ad-hoc scripts with no reliability model.

Key orchestration responsibilities:
- Workflow scheduling (time/event-driven)
- Dependency management (upstream/downstream/task graph)
- Retry/backoff and timeout policies
- Alerting and incident hooks
- Parameterization (date ranges, environments)
- Lineage + auditability of runs

---

## 2. Architecture Flow (Text Diagrams)

### Generic orchestration pattern
```text
Scheduler/Event Trigger
  → DAG/State Machine
  → Ingestion Tasks
  → Validation Tasks
  → Transform Tasks
  → Publish Tasks
  → Notification + Metrics
```

### Azure orchestration flow
```text
ADF Trigger (schedule/event)
  → Metadata-driven ADF Pipeline
  → Databricks Notebook Activities
  → Synapse Stored Procedures
  → Azure Monitor + Logic Apps alerts
```

### AWS orchestration flow
```text
EventBridge/Cron
  → Step Functions state machine
  → Glue job / EMR step / Lambda task
  → Redshift publish step
  → CloudWatch + SNS + PagerDuty
```

### GCP orchestration flow
```text
Cloud Composer (Airflow DAG)
  → Dataflow/Dataproc tasks
  → BigQuery transformations
  → Cloud Monitoring alerting
```

---

## 3. Cloud-Specific Implementations

## Azure Data Factory (ADF)
Best for enterprise ETL with metadata-driven pipelines and managed connectors.

Pattern:
1. Lookup source metadata table.
2. ForEach loops over entities.
3. Copy, transform, and load with dependency chains.
4. Retry on transient errors.
5. Webhook/Logic App notifications.

Production practices:
- global parameters per environment
- managed identity for secretless auth
- trigger windows aligned to upstream readiness

---

## Airflow (self-managed / MWAA / Composer)
Best for Python-first orchestration and custom workflows.

Recommended DAG settings:
- `retries`, `retry_delay`, `execution_timeout`
- `max_active_runs`, `depends_on_past=False` unless needed
- task-level SLA and pools for resource control

Use cases:
- cross-cloud orchestration
- mixed Spark + SQL + API workloads
- complex branching and conditional logic

---

## AWS Step Functions
Best for serverless orchestration and explicit state transitions.

Strengths:
- visual state machine and native retry/catch
- strong integration with Lambda, Glue, ECS, EMR
- deterministic control flow and failure paths

Retry example concept:
```json
{
  "Retry": [
    {
      "ErrorEquals": ["States.Timeout", "States.TaskFailed"],
      "IntervalSeconds": 10,
      "BackoffRate": 2.0,
      "MaxAttempts": 4
    }
  ]
}
```

---

## GCP Composer
Managed Airflow with deep GCP integration.

Typical pattern:
- Composer DAG triggers Dataflow templates
- waits for completion
- runs BigQuery SQL transformations
- updates data quality status table
- sends alerts via Cloud Monitoring

---

## 4. Failure Handling

Orchestration-layer controls:
- task retries with exponential backoff
- timeout + circuit breaker pattern
- checkpoint/marker tables for re-entry
- skip/recover downstream only after upstream consistency checks
- failure domains (one table failing should not kill all critical tables)
- auto-ticket creation for persistent failures

DAG/state machine anti-fragility:
- make tasks idempotent
- isolate side effects
- explicit compensation tasks for partial writes

---

## 5. Logging & Monitoring

### Azure Monitor
- ADF activity run history
- pipeline-level SLA dashboards
- alert rules for failure spikes and delay

### AWS CloudWatch
- Step Functions state transition failures
- Glue/EMR duration anomalies
- centralized logs via CloudWatch log groups

### GCP Stackdriver / Cloud Monitoring
- Composer DAG success/failure trends
- Dataflow/BigQuery job durations and error ratios

Operational KPIs:
- success rate by DAG
- median and P95 runtime
- retries per run
- mean time to recovery (MTTR)

---

## 6. Real-World Scenario

### E-commerce orchestration at scale
```text
00:30 - Trigger ingest DAG
00:40 - Validate raw completeness
01:00 - Transform orders/customers/inventory in parallel
02:00 - Publish marts
02:10 - Run reconciliation checks
02:20 - Notify BI readiness
```

Key properties:
- dependency graph with parallel branches
- hard stop on reconciliation failure
- partial rerun capability by domain (`orders`, `inventory`)

### Ride-sharing daily + streaming hybrid
- Batch settlement DAG hourly
- Streaming jobs health checks every 5 min
- On streaming lag threshold breach, fallback aggregate pipeline invoked

---

## 7. Common Mistakes

1. Monolithic DAG with 200+ tightly coupled tasks.
2. No environment promotion strategy (dev/stage/prod).
3. Triggering pipelines on schedule only, ignoring upstream freshness.
4. Hardcoding secrets/paths per task.
5. Missing failure classification (transient vs permanent).
6. No runbook for rerun/backfill.
7. Unlimited retries causing resource exhaustion.

---

## 8. Performance Tips

- Parallelize independent branches aggressively.
- Use task pools/queues to prevent noisy neighbor effects.
- Avoid orchestration engines doing heavy compute.
- Keep tasks short and composable.
- Use metadata-driven loops instead of copy-paste DAGs.
- Cap concurrent runs to protect downstream systems.
- Profile critical path and eliminate serial bottlenecks.

---

## 9. 🔥 Interview Questions (Orchestration)

### Q1. What is idempotency in orchestration?
Tasks should be rerunnable without changing final state incorrectly. Use checkpoints, MERGE semantics, and deterministic outputs.

### Q2. How do you handle late-arriving data in orchestrated workflows?
Use freshness sensors + delayed dependencies + correction DAGs. Keep mutable windows for recent partitions and run reconciliation jobs.

### Q3. What is exactly-once processing in orchestrated systems?
Exactly-once is achieved end-to-end through idempotent tasks, dedup keys, and transactional sinks, not by scheduler alone.

### Q4. How do you design fault-tolerant orchestrations?
Small idempotent tasks, explicit retries/catches, isolated failure domains, durable state checkpoints, and replay/backfill workflows.

### Additional prompts
- ADF vs Airflow vs Step Functions vs Composer: when to choose what?
- How do you prevent DAG explosion for 500 tables?
- How do you enforce SLA and alert policies consistently?
- How do you orchestrate across multi-cloud boundaries?
