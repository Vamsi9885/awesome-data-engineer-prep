# AWS Data Engineer Interview Preparation (Amazon-Level)

Act as a Senior Data Engineer and interviewer with deep expertise in AWS (Amazon-level interviews).

---

## 🎯 Goal
Prepare for AWS Data Engineer interviews with deep understanding and real-world thinking.

---

## ⚠️ Common Mistakes Candidates Make
1. Misusing **Glue vs EMR** (using Glue for heavy custom Spark workloads where EMR is better).
2. Not optimizing **S3 data layout** (no partitioning, tiny files, mixed formats).
3. Poor partitioning strategy across S3/Athena/Redshift Spectrum.
4. Ignoring schema evolution and data contracts.
5. Building pipelines without idempotency and replay strategy.
6. Treating streaming pipelines as fire-and-forget (no DLQ/checkpoint/alerts).

---

## 1. Question
What are core design principles for building a scalable data lake on S3?

## 2. Why interviewer asks this
To evaluate whether you understand practical lake architecture and not just “store files in S3.”

## 3. Detailed Answer
A scalable S3 data lake needs:
- **Zone-based design**: raw/bronze, refined/silver, curated/gold.
- **Open formats**: Parquet/ORC for analytics; avoid CSV at scale.
- **Partitioning** by high-selectivity query keys (e.g., dt, region).
- **Small-file control**: compact files to optimal size (128MB+ typical).
- **Catalog governance** via Glue Data Catalog.
- **Security**: IAM, bucket policies, KMS encryption, Lake Formation where needed.
- **Lifecycle policies** for tiering and retention.
- **Data quality and lineage** integrated from ingestion.

## 4. Real-world scenario
An e-commerce company stores clickstream, orders, and catalog data in S3. Raw JSON lands hourly, then ETL compacts to partitioned Parquet by `dt` and `marketplace` to reduce Athena scan costs by >70%.

## 5. Follow-up questions
- How do you choose partition columns?
- How would you design for late-arriving data?
- When would you use Iceberg/Hudi/Delta on AWS?

---

## 1. Question
S3 vs HDFS: what are the key differences for data engineering workloads?

## 2. Why interviewer asks this
Classic architecture comparison to test distributed storage fundamentals.

## 3. Detailed Answer
- **HDFS**: tightly coupled with compute cluster, strong data locality, block storage semantics.
- **S3**: object storage, decoupled compute/storage, massive durability, virtually infinite scale.
- S3 is better for cloud-native, multi-engine analytics; HDFS is common in legacy on-cluster Hadoop ecosystems.
- S3 lacks HDFS-style append semantics; modern table formats mitigate consistency/metadata challenges.

## 4. Real-world scenario
A legacy Hadoop platform migrated from HDFS to S3 + EMR + Athena. Compute elasticity improved, and storage costs dropped due to object lifecycle tiering.

## 5. Follow-up questions
- How do you handle rename-heavy workloads on S3?
- Why do table formats matter more on object storage?
- What is the impact on Spark job design?

---

## 1. Question
How do you optimize S3 layout for Athena and Spark query performance?

## 2. Why interviewer asks this
To test practical cost/performance tuning knowledge.

## 3. Detailed Answer
Best practices:
- Use columnar formats (Parquet/ORC) with compression (Snappy/ZSTD).
- Partition by commonly filtered columns.
- Avoid over-partitioning and tiny files.
- Enforce consistent schema and naming.
- Use partition projection where suitable.
- Periodically compact and vacuum stale objects.

## 4. Real-world scenario
Logs initially stored as hourly JSON objects caused expensive Athena scans. Converting to daily partitioned Parquet cut query runtime from minutes to seconds for common dashboards.

## 5. Follow-up questions
- How many partitions are too many?
- When should you use bucketing?
- How do you rebalance historical partitions?

---

## 1. Question
Explain AWS Glue architecture and major components.

## 2. Why interviewer asks this
To assess whether you understand Glue beyond “serverless ETL.”

## 3. Detailed Answer
Glue includes:
- **Data Catalog** (tables, partitions, schema metadata).
- **Crawlers** for schema discovery.
- **Jobs** (Spark-based ETL, Python shell).
- **Workflows/Triggers** for orchestration.
- **Glue Studio** visual development.
- **Connections** for JDBC/data sources.
It is serverless, managed Spark with DPU-based scaling, and integrates tightly with Athena/Redshift Spectrum/EMR.

## 4. Real-world scenario
A fintech team uses crawlers for external partner drops, Glue Jobs for schema normalization, and catalog tables for Athena queries consumed by analysts.

## 5. Follow-up questions
- Crawler vs manual schema registration?
- Glue bookmarks limitations?
- When to avoid Glue jobs?

---

## 1. Question
Glue vs EMR: how do you decide?

## 2. Why interviewer asks this
Mandatory trade-off question in AWS DE interviews.

## 3. Detailed Answer
- **Glue**: serverless, low-ops ETL, good for standard transformations and catalog integration.
- **EMR**: full control over Spark/Hadoop ecosystem, custom dependencies, long-running and heavy workloads.
Use Glue for quick managed ETL; use EMR when needing advanced Spark tuning, custom runtimes, or specialized frameworks.

## 4. Real-world scenario
A nightly dimension load moved to Glue for simplicity, while a 10TB skew-heavy join workflow remained on EMR with custom Spark configs and tuned executors.

## 5. Follow-up questions
- Cost break-even factors?
- How does operational overhead differ?
- Can Glue and EMR coexist in one platform?

---

## 1. Question
What is Glue Data Catalog and why is it important?

## 2. Why interviewer asks this
To verify understanding of metadata governance and multi-engine interoperability.

## 3. Detailed Answer
Glue Data Catalog is centralized metadata store for schema, partitions, locations, and table definitions. It enables consistent table abstraction for Athena, EMR, Redshift Spectrum, and Glue ETL. Good catalog hygiene prevents schema drift and query failures.

## 4. Real-world scenario
Multiple teams use shared curated datasets. Data Catalog enforces common definitions so BI and ML pipelines use the same business table schema.

## 5. Follow-up questions
- How do you manage schema evolution safely?
- How do you version contracts?
- Catalog vs Lake Formation responsibilities?

---

## 1. Question
How do Glue job bookmarks work and when can they fail?

## 2. Why interviewer asks this
To test incremental load design and reliability awareness.

## 3. Detailed Answer
Bookmarks track processed data state and help incremental processing. They can fail when source keys are unstable, files are rewritten, or partition logic changes. Always pair bookmarks with deterministic watermark logic and idempotent target writes.

## 4. Real-world scenario
A partner re-uploaded corrected files with same names. Bookmark logic skipped them; pipeline missed corrections. Fix: ingest by content hash + manifest tracking.

## 5. Follow-up questions
- How to backfill safely with bookmarks?
- Bookmark reset implications?
- Alternatives to bookmarks for CDC?

---

## 1. Question
Explain EMR architecture and major node roles.

## 2. Why interviewer asks this
To evaluate cluster-level understanding for big-data compute on AWS.

## 3. Detailed Answer
EMR consists of:
- **Primary node** (cluster manager/control).
- **Core nodes** (run tasks + store HDFS if used).
- **Task nodes** (compute-only, elastic).
It runs Spark/Hadoop/Presto/etc. You can combine On-Demand + Spot with auto-scaling policies.

## 4. Real-world scenario
A marketplace ETL runs on transient EMR clusters nightly, scaling task nodes during peak joins then terminating to save cost.

## 5. Follow-up questions
- When to use transient vs long-running clusters?
- Spot interruption mitigation?
- EMRFS consistency and S3 commit considerations?

---

## 1. Question
How do you optimize Spark jobs on EMR?

## 2. Why interviewer asks this
Optimization depth is a senior-level differentiator.

## 3. Detailed Answer
Key methods:
- Right-size executors/cores/memory.
- Reduce shuffle and skew.
- Broadcast joins where appropriate.
- Use partition pruning and predicate pushdown.
- Tune shuffle partitions and AQE.
- Avoid tiny files in source/target.
- Use efficient serialization/compression.

## 4. Real-world scenario
A 2-hour Spark job dropped to 25 minutes after repartitioning by join key, enabling AQE, and compacting small S3 files.

## 5. Follow-up questions
- How do you detect skew quickly?
- Broadcast threshold trade-offs?
- Driver OOM root causes?

---

## 1. Question
What is Athena and where does it fit in AWS analytics stack?

## 2. Why interviewer asks this
To assess query-engine selection and serverless analytics understanding.

## 3. Detailed Answer
Athena is serverless SQL on S3 (Presto/Trino-based). Best for ad-hoc analysis, lightweight reporting, and exploration over data lake. Pricing is by scanned data, so data layout strongly influences cost.

## 4. Real-world scenario
Operations analysts run ad-hoc SQL over daily partitioned Parquet logs in Athena without provisioning infrastructure.

## 5. Follow-up questions
- Athena vs EMR Presto?
- How do you reduce scanned bytes?
- When does Athena become a poor fit?

---

## 1. Question
Athena vs Redshift: how do you choose?

## 2. Why interviewer asks this
Mandatory architecture decision question.

## 3. Detailed Answer
- **Athena**: serverless, pay-per-scan, best for sporadic/ad-hoc queries over S3.
- **Redshift**: provisioned/serverless warehouse for high concurrency, predictable BI performance, complex joins and materialized models.
Use Athena for exploratory lake queries; Redshift for enterprise BI and low-latency dashboard workloads.

## 4. Real-world scenario
Data science exploratory queries run in Athena; executive KPI dashboards with strict SLAs run on Redshift with modeled marts.

## 5. Follow-up questions
- Cost model crossover point?
- Redshift Spectrum role in hybrid strategy?
- How to share datasets between both?

---

## 1. Question
Explain Redshift architecture and distribution design basics.

## 2. Why interviewer asks this
To test MPP warehousing fundamentals.

## 3. Detailed Answer
Redshift uses distributed compute nodes and columnar storage. Performance depends on:
- Distribution style/key (data colocation).
- Sort keys (range pruning).
- Compression encodings.
- WLM queue management.
Bad dist/sort choices cause heavy data shuffles and slow queries.

## 4. Real-world scenario
Fact table initially EVEN-distributed caused frequent redistribution joins. Changing DISTKEY to customer_id aligned joins with major dimensions and reduced query time significantly.

## 5. Follow-up questions
- AUTO dist/sort vs manual tuning?
- Interleaved vs compound sort key?
- How do you diagnose skew in Redshift?

---

## 1. Question
How do you optimize slow Redshift queries?

## 2. Why interviewer asks this
Scenario-based troubleshooting is core for senior DE roles.

## 3. Detailed Answer
Steps:
1. Inspect EXPLAIN plan and STL/SVL system views.
2. Check table stats and VACUUM/ANALYZE freshness.
3. Review dist/sort key alignment.
4. Eliminate unnecessary cross joins and casts.
5. Use materialized views and result caching where appropriate.
6. Tune WLM and concurrency scaling.

## 4. Real-world scenario
A monthly finance query dropped from 40 minutes to 4 minutes after sort key redesign, MV creation, and updated stats with ANALYZE.

## 5. Follow-up questions
- Vacuum frequency strategy?
- How to manage mixed ETL + BI concurrency?
- When to use Redshift Serverless?

---

## 1. Question
Kinesis Data Streams architecture: what should an interviewer expect you to know?

## 2. Why interviewer asks this
To validate streaming fundamentals in AWS.

## 3. Detailed Answer
Core concepts:
- **Stream** with multiple **shards**.
- Producers write records with partition keys.
- Consumers read via shard iterators / enhanced fan-out.
- Ordering guaranteed within shard.
Capacity planning: shards determine throughput and parallelism.

## 4. Real-world scenario
Ride telemetry ingested into Kinesis partitioned by city_id. Consumer apps independently process pricing, fraud, and monitoring pipelines.

## 5. Follow-up questions
- How do partition keys affect hot shards?
- Enhanced fan-out vs shared throughput?
- Retention and replay trade-offs?

---

## 1. Question
Kinesis vs Kafka: what are practical differences?

## 2. Why interviewer asks this
Mandatory comparison for streaming architecture interviews.

## 3. Detailed Answer
- **Kinesis**: fully managed AWS-native stream service, simpler ops, integrated with AWS ecosystem.
- **Kafka**: broader ecosystem, open-source portability, self-managed (or MSK managed) flexibility.
Choose based on ops model, portability requirements, and ecosystem integration.

## 4. Real-world scenario
A team running fully on AWS moved to Kinesis for lower operational burden and native integration with Lambda, Firehose, and CloudWatch.

## 5. Follow-up questions
- Kinesis vs MSK specifically?
- Migration concerns from Kafka topics?
- Throughput and ordering guarantees comparison?

---

## 1. Question
How do you handle streaming pipeline failures on AWS?

## 2. Why interviewer asks this
Mandatory scenario question focused on resilience.

## 3. Detailed Answer
Resilience pattern:
- Retries with backoff for transient failures.
- DLQ (SQS) for poison records.
- Checkpointing/state management.
- Idempotent sink writes.
- Lag monitoring and autoscaling.
- Replay strategy from retention window.

## 4. Real-world scenario
Fraud scoring Lambda fails on malformed events. Bad payloads go to DLQ for triage while main stream continues. Replay tool reprocesses corrected events.

## 5. Follow-up questions
- How do you guarantee no data loss?
- At-least-once implications?
- How to test replay workflows?

---

## 1. Question
When should you use Kinesis Data Firehose vs Data Streams?

## 2. Why interviewer asks this
To test service fit and operational trade-offs.

## 3. Detailed Answer
- **Firehose**: managed delivery to S3/Redshift/OpenSearch with minimal custom processing.
- **Data Streams**: custom real-time processing, multiple consumers, fine-grained control.
Use Firehose for simpler ingestion pipelines; Data Streams for complex streaming logic.

## 4. Real-world scenario
Security logs sent via Firehose to S3 every 60 seconds, while fraud events use Data Streams for sub-second custom processing.

## 5. Follow-up questions
- Firehose buffering trade-offs?
- Can Firehose transform records?
- How to combine both in one architecture?

---

## 1. Question
How does Lambda fit into data engineering pipelines?

## 2. Why interviewer asks this
To check serverless event-driven design capability.

## 3. Detailed Answer
Lambda is best for lightweight transformations, event routing, validation, and orchestration hooks. It integrates with S3/Kinesis/SQS/EventBridge/Step Functions. For heavy ETL, use Glue/EMR instead.

## 4. Real-world scenario
S3 object-created event triggers Lambda to validate schema, enrich metadata, and trigger Step Functions workflow for downstream processing.

## 5. Follow-up questions
- Lambda concurrency controls?
- Cold-start mitigation techniques?
- When to move from Lambda to container/batch compute?

---

## 1. Question
What are key Lambda limitations relevant to data workloads?

## 2. Why interviewer asks this
To ensure realistic architecture choices.

## 3. Detailed Answer
Constraints:
- Max execution duration.
- Memory/CPU coupling.
- Ephemeral storage limits.
- Payload size constraints.
- Stateless nature.
Large joins or long-running Spark-like tasks are unsuitable.

## 4. Real-world scenario
A team attempted large CSV joins in Lambda and hit timeout/memory failures. They moved heavy transforms to Glue and kept Lambda for orchestration.

## 5. Follow-up questions
- How do you choose memory size?
- Best use of Lambda layers?
- How do retries affect downstream duplicates?

---

## 1. Question
Explain Step Functions and why they matter for data pipelines.

## 2. Why interviewer asks this
To test orchestration maturity and fault-tolerant workflow design.

## 3. Detailed Answer
Step Functions orchestrate tasks with visual, stateful workflows:
- Sequential/parallel branches
- Retry/catch policies
- Wait and callback patterns
- Service integrations (Lambda, Glue, EMR, ECS, SNS, SQS)

They enable deterministic control flow and better observability than ad-hoc chained Lambdas.

## 4. Real-world scenario
Daily ETL orchestration uses Step Functions to run ingestion, validation, transformation, quality checks, and publishing with explicit failure branches and alerting.

## 5. Follow-up questions
- Standard vs Express workflows?
- How do you design compensation logic?
- Step Functions vs MWAA for orchestration?

---

## 1. Question
How to design an end-to-end AWS data pipeline for batch + streaming?

## 2. Why interviewer asks this
Mandatory system design capability check.

## 3. Detailed Answer
Reference design:
- Batch ingest via Glue/Step Functions into S3 raw.
- Streaming ingest via Kinesis Data Streams into S3/Redshift.
- Transform with Glue/EMR into curated Parquet/Iceberg.
- Query via Athena (ad-hoc) and Redshift (BI).
- Central metadata via Glue Catalog.
- Monitoring via CloudWatch + alarms.
- Security via IAM, KMS, VPC endpoints, Lake Formation.

## 4. Real-world scenario
Marketplace platform combines hourly batch order ingestion and near-real-time clickstream scoring, publishing unified marts for growth and finance teams.

## 5. Follow-up questions
- How do you enforce data contracts?
- How do you handle late data in both paths?
- What is your disaster recovery strategy?

---

## 1. Question
How would you build a data lake on AWS from scratch?

## 2. Why interviewer asks this
Mandatory scenario with architecture, governance, and operations depth.

## 3. Detailed Answer
Steps:
1. Define domain model and zones.
2. Create S3 buckets/prefix strategy.
3. Set up Glue Catalog and schema controls.
4. Build ingestion templates (batch + streaming).
5. Implement quality checks and lineage.
6. Configure IAM/KMS/Lake Formation.
7. Add cost governance and lifecycle rules.
8. Expose datasets via Athena/Redshift Spectrum.

## 4. Real-world scenario
A media company replaced siloed ETL with centralized S3 lake and reduced duplicate pipeline maintenance across 12 teams.

## 5. Follow-up questions
- Single bucket vs multi-bucket strategy?
- How do you isolate team access?
- How do you version datasets?

---

## 1. Question
How do you design partitioning strategy across S3, Glue, and Athena?

## 2. Why interviewer asks this
Poor partitioning is a frequent practical failure.

## 3. Detailed Answer
Choose partition keys based on query filters and cardinality. Typical: `dt`, `region`, `source`.
Avoid:
- Overly granular partitions causing metadata explosion.
- High-cardinality keys as partitions.
Balance with file size and compaction jobs. Keep partition evolution controlled.

## 4. Real-world scenario
Partitioning by user_id created millions of tiny partitions and slow planning. Switched to dt/region and used secondary indexes in warehouse layer.

## 5. Follow-up questions
- Partition projection vs Glue partitions?
- How to handle repartition migration?
- What metrics indicate poor partitioning?

---

## 1. Question
How do you manage schema evolution in AWS lakehouse pipelines?

## 2. Why interviewer asks this
Schema drift handling is critical in production systems.

## 3. Detailed Answer
Use schema contracts with controlled evolution:
- Detect changes at ingestion.
- Route breaking changes to quarantine.
- Support additive evolution where safe.
- Keep versioned metadata and compatibility checks.
For table formats (Iceberg/Hudi/Delta), rely on managed schema evolution features carefully.

## 4. Real-world scenario
Partner added nested field to events. Ingestion accepted raw payload, but curated job enforced contract and flagged downstream owners before promotion.

## 5. Follow-up questions
- Backward vs forward compatibility?
- How to automate schema change approval?
- How to backfill old data for new columns?

---

## 1. Question
How do you implement idempotent ETL on AWS?

## 2. Why interviewer asks this
Reliability and rerun safety are key interview signals.

## 3. Detailed Answer
Idempotency techniques:
- Deterministic keys and merge/upsert.
- Manifest tracking for processed files.
- Transactional table formats for atomic commits.
- Partition overwrite or merge with run_id lineage.
- Safe retry design with exactly-once business semantics.

## 4. Real-world scenario
Nightly ETL rerun after partial failure reprocessed only affected partitions without duplicate records due to deterministic merge keys.

## 5. Follow-up questions
- How do you test idempotency?
- At-least-once ingestion with exactly-once outputs?
- What metadata tables are needed?

---

## 1. Question
What are best practices for loading data into Redshift from S3?

## 2. Why interviewer asks this
To verify warehouse ingestion optimization skills.

## 3. Detailed Answer
Use COPY with:
- Compressed columnar files.
- Appropriate manifest and IAM role.
- Staging patterns and validation checks.
- Proper dist/sort key alignment post-load.
Batch large files rather than many tiny files.

## 4. Real-world scenario
Daily 300GB load improved by converting source to gzipped Parquet and batching COPY by partition windows.

## 5. Follow-up questions
- COPY vs INSERT trade-offs?
- How do you load CDC into Redshift?
- How do you validate load completeness?

---

## 1. Question
How do you secure AWS data pipelines end-to-end?

## 2. Why interviewer asks this
Security design is mandatory in senior interviews.

## 3. Detailed Answer
Security stack:
- IAM least privilege roles.
- KMS encryption at rest + TLS in transit.
- VPC endpoints/private networking.
- Bucket policies with explicit deny.
- Lake Formation fine-grained access.
- Secrets Manager/Parameter Store for credentials.
- Audit via CloudTrail/CloudWatch logs.

## 4. Real-world scenario
Regulated data platform enforced row/column access using Lake Formation and role-based redaction views before analytics access.

## 5. Follow-up questions
- IAM role chaining pitfalls?
- KMS key policy gotchas?
- How to audit data access trails?

---

## 1. Question
How do you control cost in AWS analytics pipelines?

## 2. Why interviewer asks this
Cost ownership is expected at Amazon-level roles.

## 3. Detailed Answer
Cost controls:
- S3 storage classes/lifecycle policies.
- Athena scan reduction (partitioning + Parquet).
- Right-sized EMR clusters + Spot usage.
- Auto-stop idle resources.
- Redshift workload and concurrency tuning.
- Monitoring cost per pipeline/domain.

## 4. Real-world scenario
Athena monthly cost dropped 60% after converting CSV to Parquet and implementing partition projection.

## 5. Follow-up questions
- How do you attribute costs per team?
- What KPIs track data platform efficiency?
- Where are hidden AWS analytics costs?

---

## 1. Question
How do you monitor and alert on AWS data pipelines?

## 2. Why interviewer asks this
Operational excellence and on-call readiness.

## 3. Detailed Answer
Use:
- CloudWatch metrics/logs/alarms.
- Step Functions execution status alerts.
- Glue job metrics and failure notifications.
- Kinesis lag/iterator age monitoring.
- Data quality SLAs (freshness/completeness) with alerting.
Integrate alerts with SNS/Slack/PagerDuty and runbooks.

## 4. Real-world scenario
An SLA alert detects delayed curated table publication and automatically opens incident with run context and failed step metadata.

## 5. Follow-up questions
- Which metrics are leading indicators?
- How to reduce alert noise?
- How to instrument data quality alerts?

---

## 1. Question
What is the role of Step Functions in failure recovery?

## 2. Why interviewer asks this
To test explicit error handling design in orchestration.

## 3. Detailed Answer
Step Functions provide retry/catch per state, branching for fallback, compensation actions, and resumable flow control. This enables robust recovery without deeply nested custom code.

## 4. Real-world scenario
If transformation fails after ingestion succeeds, workflow skips re-ingest and resumes at transform step after fix using checkpointed state machine path.

## 5. Follow-up questions
- How to design dead-letter workflows?
- Compensation patterns in distributed ETL?
- Human-in-the-loop approvals integration?

---

## 1. Question
How do you handle late-arriving and out-of-order data on AWS?

## 2. Why interviewer asks this
Real-world data latency is a common production challenge.

## 3. Detailed Answer
Use event-time processing, watermark windows, overlap backfills, and merge semantics in curated layer. Keep raw immutable and recalculate affected partitions periodically.

## 4. Real-world scenario
Delivery events arrive late by up to 48 hours. Pipeline reprocesses rolling 3-day partitions nightly to keep metrics accurate.

## 5. Follow-up questions
- How do you set overlap window size?
- How to avoid expensive full reprocessing?
- What about slowly changing dimensions?

---

## 1. Question
How do you design CDC pipelines on AWS?

## 2. Why interviewer asks this
To evaluate near-real-time update handling for operational systems.

## 3. Detailed Answer
CDC pipeline typically uses DMS/Kinesis/Kafka ingestion, raw change logs in S3, then merge into curated tables. Track operation type (I/U/D), sequence ordering, and dedup by PK+timestamp/LSN.

## 4. Real-world scenario
Order database changes stream into S3 CDC logs and nightly merge job updates Redshift dimensional models with delete handling.

## 5. Follow-up questions
- How do you preserve ordering across shards?
- Hard delete handling in lake + warehouse?
- Snapshot + CDC bootstrap approach?

---

## 1. Question
What are common anti-patterns in Glue ETL pipelines?

## 2. Why interviewer asks this
To measure practical maturity and avoidability of expensive mistakes.

## 3. Detailed Answer
Anti-patterns:
- Heavy custom Spark tuning needs forced into Glue when EMR is better.
- Excessive crawler reliance in unstable schemas.
- No bookmark validation/testing.
- Monolithic jobs without modular checkpoints.
- Writing many tiny files.

## 4. Real-world scenario
A single 5-hour Glue job failed near end and restarted from scratch repeatedly. Refactored into modular step workflows with checkpoints.

## 5. Follow-up questions
- How do you modularize Glue workflows?
- What belongs in one job vs multiple?
- How to benchmark Glue vs EMR?

---

## 1. Question
How do you choose file format and compression in AWS data lakes?

## 2. Why interviewer asks this
Foundational for storage/query performance and cost.

## 3. Detailed Answer
Prefer Parquet/ORC for analytics due to column pruning and compression. Use Snappy for faster read/write trade-off; ZSTD for better compression where CPU budget allows.

## 4. Real-world scenario
Moving from JSON to Parquet+Snappy reduced data scanned in Athena by 85% and improved latency substantially.

## 5. Follow-up questions
- ORC vs Parquet in Athena/EMR?
- Compression choice by workload?
- How to handle nested schemas?

---

## 1. Question
What is Redshift Spectrum and when should you use it?

## 2. Why interviewer asks this
Tests hybrid lake-warehouse design thinking.

## 3. Detailed Answer
Spectrum lets Redshift query external S3 data via Glue Catalog. Use it for cold/less-frequent data access while keeping hot modeled data inside Redshift tables.

## 4. Real-world scenario
Finance keeps last 12 months in Redshift local tables, older history in S3 queried via Spectrum to balance cost and access.

## 5. Follow-up questions
- Spectrum performance tuning?
- Predicate pushdown behavior?
- External table governance strategy?

---

## 1. Question
How do you manage workload isolation in Redshift?

## 2. Why interviewer asks this
To evaluate BI + ETL coexistence strategy.

## 3. Detailed Answer
Use WLM queues, query priorities, and concurrency scaling. Separate ETL heavy queries from dashboard workloads. Apply query monitoring rules to kill runaway jobs.

## 4. Real-world scenario
Morning dashboards were delayed by ETL overlap. Dedicated WLM queue and schedule shifts stabilized P95 dashboard latency.

## 5. Follow-up questions
- Auto WLM vs manual WLM?
- Concurrency scaling cost implications?
- Detecting queue bottlenecks?

---

## 1. Question
How do you design DLQ strategy for streaming on AWS?

## 2. Why interviewer asks this
To assess fault containment and replay capability.

## 3. Detailed Answer
Define DLQ per pipeline stage (SQS/S3). Include payload, error reason, attempt count, and trace IDs. Build replay tooling and redrive policies with dedup safeguards.

## 4. Real-world scenario
Malformed events routed to SQS DLQ with schema-validation error tags; corrected records replayed after parser patch.

## 5. Follow-up questions
- DLQ retention policy?
- How to prevent replay storms?
- Should DLQ be per consumer or shared?

---

## 1. Question
How do you design metadata-driven pipelines on AWS?

## 2. Why interviewer asks this
To assess reus<edit_file>
<path>data-engineer-prep/interview_preparation/TODO.md</path>
<content>
<<<<<<< SEARCH
## Azure Interview Preparation Task (New)
### Scope
- [ ] Create `azure
