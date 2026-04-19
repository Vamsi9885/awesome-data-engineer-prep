# Azure Data Engineer Interview Preparation (Senior Interviewer Edition)

Acting as a Senior Azure Data Engineer and interviewer (10+ years, product-based companies like Microsoft, Uber, Amazon), this guide focuses on depth, clarity, and real-world decision-making expected in strong interview rounds.

---

## 1. Question
What are the key components of Azure Data Factory (ADF), and how do they work together in a production pipeline?

## 2. Why interviewer asks this
To assess whether you understand ADF beyond drag-and-drop and can explain how orchestration, compute, and connectivity fit together.

## 3. Detailed Answer
ADF core components include:
- **Pipelines**: Logical grouping of activities.
- **Activities**: Units of work (Copy, Data Flow, Notebook, Stored Proc, Web, etc.).
- **Datasets**: Named views of data structure/location.
- **Linked Services**: Connection metadata to source/sink/compute.
- **Integration Runtime (IR)**: Compute and network bridge to move/transform data.
- **Triggers**: Schedule/tumbling/event/manual execution control.
- **Parameters/Variables**: Reusability and dynamic behavior.
- **Monitoring/Alerts**: Operational visibility and reliability.

In production, a pipeline is usually metadata-driven, uses parameterized datasets/linked services, routes errors to failure paths, and emits operational logs to Log Analytics/Application Insights.

## 4. Real-world scenario
A retail company ingests orders from on-prem SQL Server and SaaS APIs into ADLS Gen2 every 15 minutes. ADF uses Self-hosted IR for on-prem connectivity, event/schedule triggers, and Databricks notebook activities for transformation.

## 5. Follow-up questions
- How do linked services differ from datasets?
- Where should business rules live: ADF Data Flow or Databricks?
- How would you design ADF for 200+ source systems?

---

## 1. Question
Explain Integration Runtime (IR) types in ADF and when to use each.

## 2. Why interviewer asks this
IR misunderstanding is a common failure area in Azure interviews.

## 3. Detailed Answer
Three IR types:
- **Azure IR**: Managed by Microsoft; best for cloud-native data movement and Data Flow execution.
- **Self-hosted IR**: Installed in your VM/on-prem; required for private network/on-prem sources and sinks.
- **Azure-SSIS IR**: Dedicated runtime for lift-and-shift SSIS packages.

Selection depends on network boundaries, latency, security controls, and compatibility requirements. In enterprise setups, Self-hosted IRs are often clustered for HA and scaled horizontally.

## 4. Real-world scenario
Bank data in on-prem Oracle must move to ADLS privately. Self-hosted IR runs inside corporate network and uses private endpoint connectivity to Azure.

## 5. Follow-up questions
- How do you design Self-hosted IR high availability?
- How do you monitor IR node health?
- What bottlenecks can IR introduce?

---

## 1. Question
What is the difference between Debug run and Trigger run in ADF?

## 2. Why interviewer asks this
To validate practical pipeline lifecycle knowledge and production safety.

## 3. Detailed Answer
- **Debug run**:
  - Manual test execution from authoring.
  - Often uses current unsaved draft state.
  - Useful for quick validation and step-wise troubleshooting.
- **Trigger run**:
  - Runs published version.
  - Triggered by schedule/event/tumbling/manual trigger invocation.
  - Used in production and monitored under trigger history.

Never assume debug success equals production success unless changes are published and trigger context/parameters are validated.

## 4. Real-world scenario
Engineer tests a pipeline in debug and sees success, but nightly trigger fails because published linked service still points to older Key Vault secret reference.

## 5. Follow-up questions
- Why can debug succeed while trigger fails?
- How do you enforce release validation for published pipelines?
- How do you compare input parameters between debug and trigger runs?

---

## 1. Question
How do you implement robust parameterization in ADF?

## 2. Why interviewer asks this
To check scalability of your design and ability to avoid pipeline sprawl.

## 3. Detailed Answer
Use:
- Pipeline parameters for environment/source specifics.
- Dataset parameters for dynamic file/table paths.
- Global parameters for shared constants (env, region, retries).
- Metadata tables controlling source, sink, load type, watermark.
- Dynamic content expressions and ForEach loops.

Best practice: Build one generic ingestion pipeline driven by metadata rows rather than cloning N pipelines.

## 4. Real-world scenario
A company ingests 120 SQL tables daily. A control table stores schema/table/load type/watermark. One pipeline loops rows and executes parameterized copy jobs.

## 5. Follow-up questions
- How do you version metadata schema changes?
- How do you secure dynamic connection values?
- How do you avoid expression complexity becoming unmaintainable?

---

## 1. Question
How do you handle failures in ADF pipelines?

## 2. Why interviewer asks this
Reliability engineering is a core hiring signal for senior roles.

## 3. Detailed Answer
Failure handling strategy:
- Activity-level retry policy (count/interval/timeout).
- Dependency conditions (OnFailure/OnCompletion).
- Error routing to logging and alert pipelines.
- Idempotent writes and checkpointing.
- Dead-letter or quarantine zones in ADLS.
- Trigger rerun/backfill strategy.
- Integration with Azure Monitor alerts and incident channels.

Avoid blind retries for deterministic failures (schema mismatch/auth failure). Use categorized error handling.

## 4. Real-world scenario
API ingestion intermittently fails with 429. Pipeline uses exponential backoff retries and rate-limit-aware delay activity. Persistent failures route payload to quarantine with alert.

## 5. Follow-up questions
- How do you make reruns idempotent?
- How do you separate transient vs permanent failures?
- What metrics would you monitor for pipeline reliability?

---

## 1. Question
ADF vs Airflow: when would you choose one over the other?

## 2. Why interviewer asks this
Architecture trade-off question to judge platform judgment, not tool preference.

## 3. Detailed Answer
- **ADF strengths**:
  - Native Azure integration.
  - Low-ops managed orchestration.
  - Fast setup for enterprise ETL and connectors.
- **Airflow strengths**:
  - Code-first DAG flexibility.
  - Strong open-source ecosystem/operator extensibility.
  - Cloud-agnostic orchestration.

Choose ADF for Azure-heavy managed enterprise integration workflows. Choose Airflow where complex custom orchestration, multi-cloud neutrality, or deep Pythonic orchestration is needed.

## 4. Real-world scenario
A fintech on Azure with SAP, SQL, Blob, Databricks workloads adopts ADF for native integration and lower ops overhead. ML workflows with custom branching remain in Airflow.

## 5. Follow-up questions
- Can ADF and Airflow coexist?
- How do you migrate Airflow DAGs to ADF patterns?
- Which tool is better for CI/CD and why?

---

## 1. Question
Explain Azure Databricks architecture from interview perspective.

## 2. Why interviewer asks this
To validate Spark compute understanding in Azure context.

## 3. Detailed Answer
Azure Databricks runs Apache Spark with workspace control plane and data plane compute clusters. Key concepts:
- Driver + Executors
- Jobs clusters vs all-purpose clusters
- Auto-scaling, auto-termination
- DBFS/ADLS integration
- Unity Catalog (governance)
- Notebook/Jobs/Repos orchestration

Performance depends on partitioning, shuffle behavior, caching strategy, file sizing, and cluster configuration.

## 4. Real-world scenario
A nightly ETL with 4 TB data uses jobs cluster, Photon-enabled runtime, optimized autoscaling and Delta Lake OPTIMIZE schedule.

## 5. Follow-up questions
- Jobs cluster vs all-purpose cluster?
- How does autoscaling affect cost/performance?
- What are common driver memory failure causes?

---

## 1. Question
What is Delta Lake and why is it important in Azure data platforms?

## 2. Why interviewer asks this
To test lakehouse concepts and production reliability understanding.

## 3. Detailed Answer
Delta Lake adds:
- ACID transactions on data lake files.
- Schema enforcement and evolution.
- Time travel/versioning.
- Efficient upserts/deletes via MERGE.
- Transaction log for consistency.

It solves common data lake pain points: partial writes, inconsistent reads, and uncontrolled schema drift.

## 4. Real-world scenario
Customer profile pipeline receives CDC updates. Delta MERGE ensures upserts are atomic and replay-safe; time travel helps rollback bad deployments.

## 5. Follow-up questions
- Delta vs Parquet-only lake?
- When to use OPTIMIZE and VACUUM?
- How does Delta handle concurrent writers?

---

## 1. Question
How do you optimize a slow Databricks job?

## 2. Why interviewer asks this
Scenario depth check for performance troubleshooting capability.

## 3. Detailed Answer
Optimization playbook:
1. Profile stages (Spark UI) to identify skew/shuffle.
2. Reduce data early (column pruning/filter pushdown).
3. Use optimal join strategy (broadcast/sort-merge).
4. Repartition intelligently before wide operations.
5. Handle skew (salting/skew hints/adaptive query execution).
6. Optimize Delta files (compaction/Z-ORDER).
7. Tune cluster (executor memory/cores/runtime/Photon).

Always optimize based on measured bottleneck, not random tuning.

## 4. Real-world scenario
A 90-minute job drops to 18 minutes after fixing skewed join key, adding broadcast join, and compacting 2M tiny files into right-sized Delta files.

## 5. Follow-up questions
- How do you detect skew quickly?
- When does broadcast join hurt?
- Explain AQE benefits in Spark 3+.

---

## 1. Question
Explain partitioning strategy in ADLS and Delta tables.

## 2. Why interviewer asks this
Ignoring partitioning is a common performance and cost mistake.

## 3. Detailed Answer
Partition by columns frequently used in filters (date, region, tenant), with balanced cardinality. Avoid over-partitioning on high-cardinality keys. Combine with:
- File size optimization (target 128MB–1GB depending workload)
- Z-ORDER for multi-dimensional skipping in Delta
- Compaction routines

Partitioning strategy must align with query patterns and ingestion frequency.

## 4. Real-world scenario
Logs partitioned by `ingest_date` + `source_system` improve query costs by 70% because analysts mostly filter by date range and source.

## 5. Follow-up questions
- Date partition vs ingestion timestamp partition?
- How do you repartition historical data?
- What happens with too many small partitions?

---

## 1. Question
Describe ADLS Gen2 storage hierarchy and naming conventions.

## 2. Why interviewer asks this
To assess maintainable data lake design skills.

## 3. Detailed Answer
Common hierarchy:
- `/raw` (bronze/landing, immutable)
- `/curated` (silver, validated/transformed)
- `/serving` (gold, business-ready)

Path example:
`abfss://datalake@acct.dfs.core.windows.net/raw/sales/orders/ingest_date=YYYY-MM-DD/`

Use consistent naming for domain/entity/load type/partition keys and avoid special characters.

## 4. Real-world scenario
E-commerce platform stores clickstream, orders, and catalog in domain-based containers with lifecycle policies and quality tags.

## 5. Follow-up questions
- Container-per-domain vs shared container?
- How do you design retention policies?
- How do you isolate PII data zones?

---

## 1. Question
RBAC vs ACLs in ADLS: how do they differ and combine?

## 2. Why interviewer asks this
Security model clarity is mandatory in enterprise interviews.

## 3. Detailed Answer
- **RBAC**: Azure resource-level permissions (management/data roles).
- **ACLs**: POSIX-style file/folder-level access controls within ADLS namespace.

Typical model: grant coarse permissions with RBAC, refine path-level control with ACLs. Use AAD groups, not user-level grants, for manageability.

## 4. Real-world scenario
Data science group has read access to curated customer features folder but no access to raw PII folder via ACL boundaries.

## 5. Follow-up questions
- What is default ACL inheritance behavior?
- How do you audit effective permissions?
- Why avoid direct user ACL assignment?

---

## 1. Question
Synapse dedicated SQL pool vs serverless SQL pool: when to use which?

## 2. Why interviewer asks this
To evaluate warehouse cost/performance trade-off awareness.

## 3. Detailed Answer
- **Dedicated pool**: Provisioned MPP warehouse, predictable performance, suited for high-concurrency dashboards and modeled warehouse workloads.
- **Serverless pool**: On-demand query over lake files, pay-per-query, ideal for ad-hoc exploration and lightweight serving.

Choose based on workload predictability, latency SLAs, and cost profile.

## 4. Real-world scenario
Finance KPI dashboards use dedicated pool with curated star schema; data exploration team uses serverless over raw/curated parquet.

## 5. Follow-up questions
- How does data distribution impact dedicated pool performance?
- How do you optimize serverless file scans?
- When to materialize external tables?

---

## 1. Question
Databricks vs Synapse: how do you compare them for interview design questions?

## 2. Why interviewer asks this
To assess platform positioning and architecture reasoning.

## 3. Detailed Answer
- **Databricks** excels in advanced data engineering, Spark transformations, ML workflows, Delta Lake optimizations.
- **Synapse** offers unified analytics with SQL-first patterns, integrated warehousing, and mixed pipelines.

Many enterprises use both: Databricks for heavy transformations/data science, Synapse for serving/reporting and SQL-centric BI workloads.

## 4. Real-world scenario
Streaming + batch enrichments in Databricks write curated Delta; Synapse dedicated pool hosts dimensional marts for Power BI.

## 5. Follow-up questions
- Cost comparison under mixed workloads?
- Governance differences (Unity Catalog vs Synapse controls)?
- Can Synapse replace Databricks fully in your context?

---

## 1. Question
Explain Event Hubs architecture and partition concept.

## 2. Why interviewer asks this
To verify real-time ingestion fundamentals.

## 3. Detailed Answer
Event Hubs is a high-throughput event ingestion service. Core concepts:
- **Namespace** → **Event Hub** → **Partitions**
- Producers send events with partition keys.
- Consumers read using consumer groups and offsets.
- Ordering is guaranteed within a partition, not globally.

Partition count defines parallelism ceiling for consumers.

## 4. Real-world scenario
IoT telemetry from 2M devices is sent to Event Hubs partitioned by device group to balance throughput and preserve local order.

## 5. Follow-up questions
- How do you choose partition key?
- What happens when one partition gets hot?
- How do consumer groups isolate downstream apps?

---

## 1. Question
What are Throughput Units (TUs) in Event Hubs and why do they matter?

## 2. Why interviewer asks this
To assess scaling and cost management in streaming systems.

## 3. Detailed Answer
Throughput Units define ingress/egress capacity per namespace in standard tier. Under-provisioning causes throttling; over-provisioning wastes cost. Monitor incoming bytes, throttled requests, and consumer lag.

## 4. Real-world scenario
During sale events, event rate spikes 4x. Auto-inflate scales TUs automatically to prevent ingestion loss.

## 5. Follow-up questions
- TU vs processing units in dedicated tier?
- How do you estimate TU requirements?
- How does batching affect throughput efficiency?

---

## 1. Question
Event Hubs vs Kafka: what are practical differences in Azure interviews?

## 2. Why interviewer asks this
To evaluate conceptual parity and managed service understanding.

## 3. Detailed Answer
Event Hubs provides Kafka protocol compatibility but differs operationally:
- Fully managed PaaS on Azure
- Native Azure security/monitoring integration
- Different quota/capacity semantics vs self-managed Kafka
- Strong option for teams prioritizing reduced ops

Kafka may be preferred for portable ecosystem/tooling or multi-cloud self-managed architecture.

## 4. Real-world scenario
An org migrates from self-hosted Kafka to Event Hubs Kafka endpoint to reduce operational burden while retaining producer/consumer protocol compatibility.

## 5. Follow-up questions
- What Kafka features are not 1:1?
- Migration pitfalls from Kafka to Event Hubs?
- How do retention and compaction compare?

---

## 1. Question
How do Azure Functions fit into data engineering pipelines?

## 2. Why interviewer asks this
To test serverless event-driven design ability.

## 3. Detailed Answer
Azure Functions are ideal for lightweight event-driven tasks:
- Trigger on Event Hubs/Blob/HTTP/Timer
- Data validation, routing, enrichment
- Calling APIs/webhooks
- Orchestration handoff to ADF/Databricks

Use Durable Functions for stateful orchestrations requiring checkpoints/retries.

## 4. Real-world scenario
A Blob-triggered Function validates schema and writes metadata to control table before triggering ADF ingestion.

## 5. Follow-up questions
- Function cold start mitigation?
- Durable Functions vs Logic Apps?
- When not to use Functions in DE pipelines?

---

## 1. Question
How do Logic Apps differ from Azure Functions in workflow design?

## 2. Why interviewer asks this
To understand low-code workflow vs code-centric event processing choices.

## 3. Detailed Answer
- **Logic Apps**: Connector-rich, declarative orchestration, strong for integrations and approvals.
- **Functions**: Code-heavy, flexible transformations, custom logic and compute control.

Logic Apps for SaaS integration workflows; Functions for custom compute-intensive or code-first handlers.

## 4. Real-world scenario
Order failure alerts are routed through Logic Apps to Teams/Jira/Email with conditional branches; complex payload transformation is handled by Functions.

## 5. Follow-up questions
- Cost trade-offs between both?
- How to combine Logic Apps and Functions?
- Monitoring strategy for hybrid workflow chains?

---

## 1. Question
Design an end-to-end Azure batch pipeline for enterprise data platform.

## 2. Why interviewer asks this
System thinking and architecture articulation are key senior signals.

## 3. Detailed Answer
Reference architecture:
1. Sources (DBs/APIs/files/on-prem)
2. Ingestion via ADF (Self-hosted IR if needed)
3. Land raw in ADLS (bronze)
4. Databricks transformation to silver/gold Delta
5. Serve via Synapse dedicated/serverless
6. Orchestration and monitoring with ADF + Azure Monitor
7. Security via Managed Identity, Key Vault, RBAC/ACL

Include data quality checks, schema evolution handling, and backfill strategy.

## 4. Real-world scenario
Global marketplace ingests catalog/pricing/inventory from 30 regions nightly and publishes conformed gold tables for BI by 6 AM regional SLA.

## 5. Follow-up questions
- How do you support CDC and late data?
- Where do you place data quality gates?
- How do you manage multi-environment CI/CD?

---

## 1. Question
How do you debug a failing ADF pipeline systematically?

## 2. Why interviewer asks this
Scenario-based debugging differentiates practical engineers.

## 3. Detailed Answer
Steps:
1. Check failed activity output/error code.
2. Validate inputs/parameters at run time.
3. Confirm linked service auth/network connectivity.
4. Check IR status and node health.
5. Validate schema/path existence.
6. Replay in debug with controlled sample.
7. Apply fix and rerun failed path idempotently.

Always classify failure category: connectivity, auth, data, transformation, infra throttling.

## 4. Real-world scenario
Pipeline fails on copy due to changed source schema (column rename). Engineer adds schema drift handling and contract alerting to prevent silent failures.

## 5. Follow-up questions
- How do you avoid recurring schema-related outages?
- Which logs are most useful in ADF debugging?
- How do you automate root-cause tagging?

---

## 1. Question
How do you design real-time Azure data pipeline?

## 2. Why interviewer asks this
Checks streaming architecture capability and latency thinking.

## 3. Detailed Answer
Typical design:
- Producers -> Event Hubs
- Stream processing via Databricks Structured Streaming or Azure Stream Analytics
- Persist to Delta in ADLS
- Serve low-latency tables to Synapse/Power BI
- Alerting via Functions/Logic Apps

Include exactly-once/at-least-once semantics discussion, checkpointing, watermarking, and late event handling.

## 4. Real-world scenario
Fraud detection pipeline ingests card swipes in Event Hubs, scores risk in near real-time, and emits high-risk events to Function for immediate action.

## 5. Follow-up questions
- How do you handle out-of-order events?
- What checkpoint strategy would you use?
- How do you balance latency vs cost?

---

## 1. Question
How do you implement incremental loads in Azure pipelines?

## 2. Why interviewer asks this
Incremental processing is essential for scalable production systems.

## 3. Detailed Answer
Approaches:
- Watermark columns (`last_updated_at`)
- CDC-based ingestion
- Delta MERGE into target
- Metadata table storing last successful watermark per entity
- Backfill window to absorb late data

Combine with idempotent write logic and replay-safe pipeline execution.

## 4. Real-world scenario
Orders table ingests 500M rows/day. Incremental pull by update timestamp with 2-day overlap backfill prevents misses due to source clock drift.

## 5. Follow-up questions
- How do you handle hard deletes?
- Watermark corruption recovery strategy?
- CDC vs timestamp-based loads trade-offs?

---

## 1. Question
How do you ensure idempotency in Azure Data Engineering workflows?

## 2. Why interviewer asks this
To evaluate production reliability under reruns and failures.

## 3. Detailed Answer
Idempotency methods:
- Deterministic target keys
- Upsert/merge instead of blind append
- Transactional writes (Delta)
- Batch/run IDs with dedup logic
- Reprocessing windows with overwrite partition strategy

A rerun should not duplicate or corrupt outputs.

## 4. Real-world scenario
Nightly pipeline rerun after partial failure safely reprocesses affected date partitions using replaceWhere in Delta and audit checks.

## 5. Follow-up questions
- How do you prove idempotency in tests?
- Append-only cases: how do you deduplicate downstream?
- How does idempotency change in streaming?

---

## 1. Question
How do you secure secrets and credentials in Azure data pipelines?

## 2. Why interviewer asks this
Security fundamentals are mandatory in product companies.

## 3. Detailed Answer
Use:
- Azure Key Vault for secrets
- Managed Identities over service principals when possible
- Private endpoints and restricted network access
- Least-privilege RBAC/ACL
- Rotation policies and secret versioning

Never hardcode credentials in notebooks/pipeline JSON.

## 4. Real-world scenario
ADF linked services use managed identity and Key Vault references; no plaintext secrets in Git repositories.

## 5. Follow-up questions
- Managed Identity vs Service Principal?
- How do you rotate secrets with zero downtime?
- How do you enforce policy for secret usage?

---

## 1. Question
How do you manage schema evolution in ADLS + Databricks pipelines?

## 2. Why interviewer asks this
Schema drift handling is a frequent operational challenge.

## 3. Detailed Answer
Use explicit contracts plus controlled evolution:
- Bronze allows drift capture.
- Silver enforces expected schema with validation.
- Delta schema evolution (`mergeSchema`) used cautiously.
- Contract tests and alerting for breaking changes.

Prefer fail-fast for critical contracts, permissive ingest for exploratory domains.

## 4. Real-world scenario
Source adds nullable field unexpectedly. Bronze captures raw record, silver model updates via reviewed schema migration pipeline.

## 5. Follow-up questions
- When should schema drift cause hard failure?
- How to backfill old partitions with new schema?
- How to version schemas across teams?

---

## 1. Question
How do you choose between ADF Data Flows and Databricks for transformation?

## 2. Why interviewer asks this
Tool selection based on complexity/cost/team skill is a common architecture probe.

## 3. Detailed Answer
- **ADF Data Flows**: Good for moderate visual transformations, low-code teams.
- **Databricks**: Better for complex logic, large-scale Spark optimization, reusable code, ML integration.

Decision factors: data volume, transformation complexity, operational standards, team expertise, and debugging needs.

## 4. Real-world scenario
Small CSV harmonization remains in Data Flows; heavy joins with CDC SCD2 logic moved to Databricks for performance and maintainability.

## 5. Follow-up questions
- Cost comparison approach?
- How do you test Data Flow logic in CI?
- Can both coexist in one pipeline?

---

## 1. Question
How do you design SCD Type 2 in Azure Databricks with Delta?

## 2. Why interviewer asks this
To assess dimensional modeling plus implementation capability.

## 3. Detailed Answer
Maintain dimension with:
- Surrogate key
- business key
- effective_start/end
- is_current flag

Use MERGE:
- expire existing current row when attribute changes
- insert new current row
- preserve history

Handle late arriving dimension updates and ensure deterministic comparison logic.

## 4. Real-world scenario
Customer tier changes from Silver to Gold. Previous row end-dated; new row inserted with current flag, enabling accurate historical revenue reporting.

## 5. Follow-up questions
- How to optimize SCD2 MERGE on large tables?
- How do you detect no-op updates?
- Type 1 vs Type 2 in same table strategy?

---

## 1. Question
How do you optimize Delta Lake tables over time?

## 2. Why interviewer asks this
Long-term table health and cost/performance maturity check.

## 3. Detailed Answer
Optimization toolkit:
- OPTIMIZE for file compaction
- Z-ORDER for selective query speed
- VACUUM for stale file cleanup (with retention policy discipline)
- Partition review based on query behavior
- Data skipping stats and auto-optimize settings

Avoid overusing small writes and uncontrolled compaction frequency.

## 4. Real-world scenario
Daily ingest produced millions of small files. Weekly OPTIMIZE plus tuned write batch size reduced query latency by 60%.

## 5. Follow-up questions
- VACUUM risks with long-running readers?
- Z-ORDER vs partitioning decisions?
- How to schedule maintenance jobs safely?

---

## 1. Question
How do you monitor end-to-end Azure data pipelines?

## 2. Why interviewer asks this
Operations excellence is expected in senior interviews.

## 3. Detailed Answer
Monitoring layers:
- ADF pipeline/activity run metrics
- Databricks job and cluster metrics
- Event Hubs lag/throughput
- Data quality metrics (freshness, completeness, null rates)
- Business SLA metrics (data arrival by cutoff times)

Centralize observability in Azure Monitor/Log Analytics; define SLOs and alert severity levels.

## 4. Real-world scenario
A “gold table freshness” alert triggers when pipeline delays exceed 20 minutes, auto-creating incident tickets and paging on-call.

## 5. Follow-up questions
- Which metrics are leading indicators of failure?
- How do you reduce alert fatigue?
- How do you monitor data correctness beyond job success?

---

## 1. Question
How do you design retry and backoff strategy for external API ingestion in ADF?

## 2. Why interviewer asks this
Tests resilience for unstable dependencies.

## 3. Detailed Answer
Use:
- Retry with exponential backoff for 429/5xx
- Circuit-breaker-like thresholding to avoid source overload
- Rate limiting and pagination checkpoints
- Dead-letter failed payloads for replay

Track request IDs for traceability and exactly-once replay semantics.

## 4. Real-world scenario
Payment gateway API occasionally throttles. Pipeline retries with jitter and writes failed requests to retry queue for controlled replay.

## 5. Follow-up questions
- Which errors should not be retried?
- How do you avoid duplicate downstream records?
- How do you estimate API throughput budget?

---

## 1. Question
How do you handle small files problem in ADLS/Delta ecosystem?

## 2. Why interviewer asks this
Performance tuning and lake housekeeping are practical skills.

## <create_file>
<path>data-engineer-prep/interview_preparation/azure_interview_preparation.md</path>
<content># 🎯 Azure Data Engineer Interview Preparation
## Act as Senior Azure Data Engineer (10+ years @ Microsoft, Uber, Amazon)

**Prepared by: Senior Azure Data Engineer with 10+ years experience across product companies**
**Goal: Crack Azure Data Engineer interviews with deep technical understanding, real-world scenarios, and confident explanations**

---

## 📋 How Azure Data Engineer Interviews Work
**Senior interviewers evaluate:**
1. **Architecture decisions** - Cost, scale, reliability trade-offs
2. **Production experience** - Failure modes, debugging, optimization
3. **Integration patterns** - How services work together
4. **Cost optimization** - Real dollar impact awareness
5. **Security/compliance** - Enterprise requirements

**Common failure patterns:**
- Not understanding Integration Runtime (IR) types deeply
- Generic "use ADF for everything" answers
- Ignoring partitioning/Z-ordering in Databricks
- Missing cost implications of serverless vs dedicated
- Poor failure recovery design

---

## ⚠️ TOP COMMON MISTAKES (Avoid These!)
1. **IR Confusion**: Thinking Self-Hosted IR = Managed VNet IR
2. **Ignoring Partitioning**: Loading 1TB data without partition pruning
3. **Poor Pipeline Design**: No parameterization, hardcoded values
4. **Delta Lake Neglect**: Not using OPTIMIZE/ZORDER
5. **Event Hubs Sizing**: Wrong partition/throughput unit choices
6. **Synapse Pool Choice**: Using dedicated for ad-hoc queries

---

## 1. Question: Explain Azure Data Factory (ADF) pipeline execution model
### Why interviewer asks this
Tests fundamental understanding of ADF's distributed execution and debugging capabilities.

### Detailed Answer
**Pipeline** → **Activity** → **Dataset** → **Linked Service** → **Integration Runtime (IR)**

**Execution flow:**
```
Pipeline Trigger → Pipeline Run ID → Activity Runs → Dataset reads/writes
```
- **Debug runs**: Interactive, single activity execution, no trigger needed
- **Trigger runs**: Scheduled/tumbling/event-based, full pipeline execution
- **IR Types**:
  | Type | Use Case | Scale | Cost |
  |------|----------|-------|------|
  | AutoResolve | Default, cloud services | Auto | Pay-per-use |
  | Managed VNet | Private networks | Fixed | Fixed/hour |
  | Self-Hosted | On-prem/VM | Manual | VM cost |

**Key differences Debug vs Trigger:**
- Debug: `@pipeline().TriggerName = null`
- Trigger: Full lineage, monitoring, retry policies

### Real-world scenario
**Uber ride pricing pipeline failure**: Debug run works (AutoResolve IR), trigger run fails (VNet IR timeout). Root cause: VNet IR subnet exhausted. Fix: Scale VNet IR nodes + parameterize node count.

### Follow-up questions
- How do you pass parameters between pipelines?
- Difference between `ForEach` parallel vs sequential?
- How to implement custom retry logic?

---

## 2. Question: ADF vs Airflow - When to choose each?
### Why interviewer asks
