# GCP Data Engineer Interview Preparation (Google-Level)

Act as a Senior Data Engineer and interviewer with deep expertise in GCP.

---

## 🎯 Goal
Prepare for GCP Data Engineer interviews with deep conceptual clarity, system design depth, and real-world production decision-making.

---

## ⚠️ Common Mistakes Candidates Make
1. Not understanding **BigQuery pricing** (on-demand bytes scanned vs slots/reservations).
2. Poor partitioning/clustering choices in BigQuery.
3. Misusing **Dataflow vs Dataproc**.
4. Treating Pub/Sub as fire-and-forget without DLQ/replay strategy.
5. Weak handling of streaming late/out-of-order events.
6. Designing pipelines without idempotency and backfill plans.

---

## 1. Question
How do you design a scalable, cost-efficient data lake/warehouse architecture on GCP?

## 2. Why interviewer asks this
To test end-to-end architecture thinking across ingestion, storage, processing, serving, governance, and cost.

## 3. Detailed Answer
A robust GCP architecture usually includes:
- **Cloud Storage** as raw/bronze immutable landing.
- **Dataflow** for stream/batch ingestion and transformation.
- **BigQuery** for curated analytics serving.
- **Pub/Sub** for decoupled event ingestion.
- **Composer** for orchestration and SLA workflows.
- **Bigtable** for low-latency key-value serving use cases.
Design principles:
- Separate raw/refined/curated zones.
- Columnar formats in lake (Parquet/Avro) where useful.
- BigQuery partitioning + clustering aligned with query patterns.
- Idempotent writes and replay/backfill support.
- Centralized observability (Cloud Logging/Monitoring) and DQ checks.
- IAM least privilege + CMEK where compliance requires.

## 4. Real-world scenario
A ride-sharing company ingests trip, clickstream, and pricing events via Pub/Sub + Dataflow. Raw events land in Cloud Storage, curated aggregates go to BigQuery for BI, while active driver location state is served from Bigtable.

## 5. Follow-up questions
- How do you choose between Bigtable and BigQuery for a workload?
- Where would you enforce schema contracts?
- What is your DR and backfill strategy?

---

## 1. Question
BigQuery vs Redshift vs Snowflake: how do you choose?

## 2. Why interviewer asks this
Mandatory warehouse comparison to assess platform-neutral reasoning.

## 3. Detailed Answer
- **BigQuery**: serverless MPP, strong GCP integration, excellent for elastic analytics and mixed batch/stream SQL workloads. Pricing by on-demand bytes or slot commitments.
- **Redshift**: tightly integrated with AWS, provisioned/serverless modes, strong for predictable BI on AWS ecosystems.
- **Snowflake**: cloud-agnostic architecture, compute-storage separation per virtual warehouse, strong data sharing/cross-cloud patterns.
Decision criteria:
1. Cloud ecosystem fit.
2. Concurrency + SLA patterns.
3. Cost profile (steady vs bursty).
4. Governance and data sharing requirements.
5. Existing team expertise and operational model.

## 4. Real-world scenario
A GCP-native fintech moved from mixed tools to BigQuery to simplify operations and leverage native streaming inserts + Dataflow integration, reducing operational overhead.

## 5. Follow-up questions
- When does BigQuery reservation pricing beat on-demand?
- BigQuery BI Engine vs materialized views?
- How do migration risks differ across the three?

---

## 1. Question
Explain BigQuery architecture and why it scales.

## 2. Why interviewer asks this
To verify foundational understanding beyond “serverless SQL.”

## 3. Detailed Answer
BigQuery separates storage/compute and uses Dremel execution trees. Key strengths:
- Columnar storage and predicate pruning.
- Distributed execution across slots.
- Automatic scaling for concurrent queries.
- Native support for nested/repeated schema.
- Managed metadata, security, and audit integration.
Performance relies heavily on data layout (partitioning/clustering), query design, and bytes scanned control.

## 4. Real-world scenario
An ad-tech team ran petabyte-scale clickstream analytics with BigQuery, using partitioned and clustered tables to maintain sub-minute dashboard queries.

## 5. Follow-up questions
- How are slots consumed by query stages?
- What causes query shuffle bottlenecks?
- How do nested fields affect performance?

---

## 1. Question
How does BigQuery pricing work, and how do you optimize cost?

## 2. Why interviewer asks this
Cost awareness is a core signal for senior data engineering roles.

## 3. Detailed Answer
Pricing dimensions:
- **Storage**: active vs long-term.
- **Query compute**: on-demand bytes scanned or flat-rate/editions slot capacity.
- **Streaming ingestion** (if applicable), plus other features (BI Engine, ML, etc.).
Cost optimization:
- Partition and cluster correctly.
- Avoid `SELECT *`; project only needed columns.
- Use partition filters and require partition filter on large tables.
- Materialize expensive recurring transformations.
- Monitor INFORMATION_SCHEMA and billing exports.
- Use reservations for stable, high-volume workloads.

## 4. Real-world scenario
A team reduced BigQuery spend 45% by converting wide ad-hoc queries into scheduled materialized marts and enforcing partition filter policies.

## 5. Follow-up questions
- On-demand vs reservations break-even?
- How do you allocate slot commitments by team?
- How do you prevent analyst anti-pattern queries?

---

## 1. Question
Partitioning vs clustering in BigQuery: how do you decide?

## 2. Why interviewer asks this
Partitioning mistakes are one of the most common production failures.

## 3. Detailed Answer
- **Partitioning**: coarse data pruning (time/date/int range).
- **Clustering**: intra-partition organization by high-cardinality filter/join columns.
Use partitioning when filters reliably include partition column; add clustering for secondary pruning and better scan efficiency.
Avoid over-partitioning and poorly selective cluster keys.

## 4. Real-world scenario
Order analytics table partitioned by `order_date`, clustered by `customer_id, country` reduced average scanned bytes significantly for daily BI workloads.

## 5. Follow-up questions
- How many clustering columns are practical?
- When repartitioning is needed, how do you migrate safely?
- What metrics prove partition strategy is failing?

---

## 1. Question
How do you optimize slow BigQuery queries systematically?

## 2. Why interviewer asks this
Tests practical troubleshooting depth.

## 3. Detailed Answer
Approach:
1. Review execution details (stages, shuffle, skew).
2. Reduce scanned data (filters/column pruning).
3. Pre-aggregate before large joins where possible.
4. Use approximate functions for exploratory analytics.
5. Replace repeated CTE-heavy logic with materialized tables/views if needed.
6. Validate join cardinalities and key quality.
7. Use clustering/partitioning aligned with frequent access paths.

## 4. Real-world scenario
A monthly finance query dropped from 22 minutes to under 3 minutes after partition pruning fixes, pre-aggregation, and eliminating unnecessary full table joins.

## 5. Follow-up questions
- How to diagnose data skew in BigQuery?
- When to use materialized views?
- How do you tune for concurrency-heavy workloads?

---

## 1. Question
What are BigQuery materialized views, and when should you use them?

## 2. Why interviewer asks this
To evaluate modeling strategy for performance and cost control.

## 3. Detailed Answer
Materialized views store precomputed results for eligible query patterns, enabling incremental refresh and lower query cost/latency for repetitive aggregations.
Use for stable KPI aggregations frequently queried by BI tools.
Do not overuse when source churn is extreme or query patterns are highly dynamic.

## 4. Real-world scenario
A retail dashboard with hourly sales aggregates moved to materialized views, cutting dashboard latency from ~20s to ~3s.

## 5. Follow-up questions
- Limitations of materialized views in BigQuery?
- Materialized views vs scheduled table builds?
- How to monitor refresh lag?

---

## 1. Question
How do you manage schema evolution in BigQuery pipelines?

## 2. Why interviewer asks this
Schema drift handling is critical in real systems.

## 3. Detailed Answer
Use contract-driven ingestion:
- Allow additive non-breaking changes where approved.
- Quarantine breaking schema changes.
- Version schemas and enforce validation in ingestion layer (Dataflow/Cloud Functions).
- Keep raw immutable payloads to support reprocessing.
- Use backfill workflows for column introduction where required.

## 4. Real-world scenario
A payments partner added nested optional fields; ingestion accepted raw payload but curated model rollout followed contract checks and controlled migration.

## 5. Follow-up questions
- Backward vs forward compatibility in events?
- How to backfill historical rows for new columns?
- How do you communicate schema change governance to producers?

---

## 1. Question
Dataflow vs Spark: how do you decide?

## 2. Why interviewer asks this
Mandatory trade-off question for GCP data engineering interviews.

## 3. Detailed Answer
- **Dataflow (Apache Beam)**:
  - Fully managed autoscaling stream/batch runtime.
  - Strong event-time/windowing/watermark semantics.
  - Lower ops burden and deep GCP integration.
- **Spark (often on Dataproc)**:
  - Broad ecosystem, flexible libraries, extensive custom tuning.
  - Often strong choice for heavy batch ETL and existing Spark codebases.
Choose Dataflow for managed streaming and unified Beam model; choose Spark/Dataproc for Spark-native workloads requiring custom cluster/runtime control.

## 4. Real-world scenario
An IoT stream processing platform moved from self-managed Spark streaming to Dataflow to reduce operational incidents and improve watermark correctness.

## 5. Follow-up questions
- Beam portability: when does it matter?
- Spark Structured Streaming vs Dataflow for low latency?
- Cost comparison methodology between both?

---

## 1. Question
Explain Apache Beam concepts used in Dataflow interviews.

## 2. Why interviewer asks this
To verify true Dataflow competency, not just managed-service familiarity.

## 3. Detailed Answer
Core Beam concepts:
- **PCollection** (data abstraction).
- **Transforms** (ParDo, GroupByKey, Combine, etc.).
- **Windowing** (fixed, sliding, session).
- **Watermarks** (event-time progress estimation).
- **Triggers** (when results are emitted).
- **State and timers** for advanced streaming logic.
Correctness in streaming depends on thoughtful event-time design, lateness handling, and idempotent sinks.

## 4. Real-world scenario
Fraud scoring uses session windows with custom triggers to balance rapid detection with late event reconciliation.

## 5. Follow-up questions
- Allowed lateness implications?
- Early vs late firing trade-offs?
- How do stateful DoFns affect scaling?

---

## 1. Question
How does Dataflow autoscaling work, and what are caveats?

## 2. Why interviewer asks this
To assess operational understanding of managed compute behavior.

## 3. Detailed Answer
Dataflow autoscaling adjusts workers based on backlog, throughput, and processing characteristics.
Caveats:
- Hot keys can still bottleneck despite more workers.
- Stateful steps and external sink limits may constrain throughput.
- Aggressive scaling can increase cost if pipeline logic is inefficient.
Use resource hints, key distribution strategies, and sink throttling awareness.

## 4. Real-world scenario
A clickstream pipeline scaled workers automatically during campaign spikes, but hot-key skew at one aggregation step caused lag; key randomization fixed bottleneck.

## 5. Follow-up questions
- How do you detect autoscaling inefficiency?
- When to set max workers aggressively?
- How does Streaming Engine change ops characteristics?

---

## 1. Question
How do you handle exactly-once semantics in Dataflow pipelines?

## 2. Why interviewer asks this
Reliability and correctness in streaming is a senior-level differentiator.

## 3. Detailed Answer
True end-to-end exactly-once depends on source, pipeline, and sink behavior.
Patterns:
- Use dedup keys/event IDs.
- Idempotent sink writes (MERGE/upsert semantics).
- Deterministic windowing and replay-safe aggregations.
- DLQ paths for poison records.
Often practical target is at-least-once ingestion with exactly-once business outcomes.

## 4. Real-world scenario
Payment events occasionally replayed by producer; Dataflow deduplicated by event_id and wrote idempotent upserts to BigQuery curated tables.

## 5. Follow-up questions
- Dedup TTL strategy?
- How to validate no duplicate business outcomes?
- What changes if sink is Bigtable vs BigQuery?

---

## 1. Question
How do you design and operate dead-letter handling in Dataflow?

## 2. Why interviewer asks this
To test production resilience and operability.

## 3. Detailed Answer
DLQ design:
- Capture payload + error metadata + processing stage + timestamp.
- Route malformed/non-retriable records to DLQ (Pub/Sub/Cloud Storage).
- Separate transient retries from permanent failures.
- Build replay tooling with dedup safeguards.
- Alert on DLQ volume anomalies.

## 4. Real-world scenario
Malformed mobile events were routed to DLQ Cloud Storage bucket, triaged daily, and replayed after parser fix without duplicating downstream metrics.

## 5. Follow-up questions
- Per-stage vs centralized DLQ?
- How to prevent replay storms?
- What retention policy should DLQ use?

---

## 1. Question
Dataproc vs Databricks: how do you choose?

## 2. Why interviewer asks this
Mandatory comparison to assess multi-platform architectural judgement.

## 3. Detailed Answer
- **Dataproc**: managed Spark/Hadoop on GCP, flexible cluster control, good for existing Spark jobs and open-source stack fidelity.
- **Databricks**: unified analytics platform with strong developer UX, optimizations, and governance/tooling ecosystem (vendor-specific depending deployment).
On GCP interviews, explain based on:
- ecosystem fit,
- operational overhead,
- optimization/tooling needs,
- portability and cost model.

## 4. Real-world scenario
A team with heavy open-source Spark dependencies chose Dataproc autoscaling clusters + ephemeral jobs to keep compatibility and control cost.

## 5. Follow-up questions
- Dataproc Serverless vs cluster mode?
- How to compare TCO across both?
- Migration challenges between platforms?

---

## 1. Question
When should you use Dataproc instead of Dataflow?

## 2. Why interviewer asks this
To test whether you can correctly map workload to processing engine.

## 3. Detailed Answer
Use **Dataproc** when:
- You already have Spark/Hadoop jobs and libraries.
- You need custom runtime dependencies and fine-grained Spark tuning.
- Workload is predominantly heavy batch ETL/ML prep.
Use **Dataflow** for managed event-time streaming and Beam-native portability with lower cluster ops burden.

## 4. Real-world scenario
A legacy Spark ETL with custom UDF jars and complex joins stayed on Dataproc while real-time enrichment moved to Dataflow.

## 5. Follow-up questions
- How do you split responsibilities between both engines?
- What are anti-patterns in mixed-engine architectures?
- How would you phase migration from Dataproc to Dataflow?

---

## 1. Question
How do you optimize Spark jobs on Dataproc?

## 2. Why interviewer asks this
Senior interviews expect hands-on performance tuning ability.

## 3. Detailed Answer
Key levers:
- Right-size executors/memory/cores.
- Use AQE and broadcast joins appropriately.
- Repartition to control shuffle skew.
- Avoid tiny files; compact output.
- Tune dynamic allocation and autoscaling policies.
- Use efficient formats (Parquet/ORC), partition pruning, predicate pushdown.

## 4. Real-world scenario
A nightly job dropped from 3.5 hours to 50 minutes after skew mitigation, adaptive execution tuning, and small-file compaction.

## 5. Follow-up questions
- How to detect skew quickly?
- Broadcast join pitfalls?
- What Dataproc metrics are most actionable?

---

## 1. Question
What is Pub/Sub architecture and delivery semantics?

## 2. Why interviewer asks this
To verify messaging fundamentals for real-time pipelines.

## 3. Detailed Answer
Pub/Sub core model:
- Topics, subscriptions, publishers, subscribers.
- Push/pull delivery options.
- At-least-once delivery by default; duplicates possible.
- Ordering keys provide ordered delivery per key (with constraints).
- Ack deadlines and retries drive delivery behavior.
Design consumers for idempotency and observability.

## 4. Real-world scenario
Ride event publishers write to Pub/Sub topic; separate subscriptions feed fraud detection, ETA prediction, and analytics pipelines independently.

## 5. Follow-up questions
- Push vs pull subscription trade-offs?
- Ordering key limitations?
- How do you tune ack deadlines safely?

---

## 1. Question
Pub/Sub vs Kafka: what are practical differences?

## 2. Why interviewer asks this
Mandatory streaming comparison in modern data interviews.

## 3. Detailed Answer
- **Pub/Sub**: fully managed, serverless messaging, minimal broker ops, deep GCP integration.
- **Kafka**: rich ecosystem and portability, explicit partition/broker control, self-managed or managed variants.
Choose Pub/Sub for low-ops GCP-native eventing; choose Kafka when ecosystem portability/custom broker behavior is critical.

## 4. Real-world scenario
A GCP-first startup replaced self-managed Kafka with Pub/Sub to reduce on-call burden while keeping decoupled event-driven services.

## 5. Follow-up questions
- Pub/Sub Lite vs Kafka for cost-sensitive workloads?
- Exactly-once considerations across both?
- Migration strategy from Kafka topics to Pub/Sub topics?

---

## 1. Question
How do you design a real-time pipeline using Pub/Sub on GCP?

## 2. Why interviewer asks this
Mandatory scenario to evaluate end-to-end streaming design ability.

## 3. Detailed Answer
Typical design:
1. Producers publish events to Pub/Sub.
2. Dataflow streaming pipeline validates/enriches/events-time windows.
3. Valid stream to BigQuery curated tables.
4. Invalid events to DLQ (Pub/Sub or Cloud Storage).
5. Monitoring for subscriber lag, throughput, DQ, and SLA freshness.
6. Replay mechanism from raw immutable storage when needed.

## 4. Real-world scenario
E-commerce clickstream pipeline processes 150K events/sec; Dataflow computes near-real-time funnel metrics in BigQuery while malformed payloads go to DLQ.

## 5. Follow-up questions
- How do you support schema versioning?
- How do you replay only affected windows?
- How do you protect against downstream backpressure?

---

## 1. Question
How do you handle streaming failures in GCP pipelines?

## 2. Why interviewer asks this
Mandatory resilience scenario; tests production reliability maturity.

## 3. Detailed Answer
Failure handling framework:
- Retries with exponential backoff for transient errors.
- DLQ for poison records.
- Checkpoint/state management in stream processor.
- Idempotent sink writes.
- Alerting on lag, error rate, stale output.
- Replay/backfill workflows with deterministic dedup.
- Runbooks and incident response drills.

## 4. Real-world scenario
A schema rollout introduced malformed events; pipeline isolated failures to DLQ while healthy traffic continued. Post-fix replay restored missing aggregates without duplication.

## 5. Follow-up questions
- How do you guarantee no data loss?
- What metrics detect silent data corruption?
- How do you test replay paths before incidents?

---

## 1. Question
What is Cloud Storage’s role in GCP data engineering architecture?

## 2. Why interviewer asks this
To test foundational storage-layer understanding.

## 3. Detailed Answer
Cloud Storage provides durable, scalable object storage for:
- raw landing zone,
- replay source of truth,
- archive/cold data,
- batch exchange files.
Best practices:
- deterministic folder conventions,
- immutable raw writes,
- lifecycle and retention policies,
- bucket-level security controls and CMEK where required.

## 4. Real-world scenario
A media platform stores immutable raw event logs in Cloud Storage for 90-day replay, while curated analytics reside in BigQuery.

## 5. Follow-up questions
- Multi-bucket vs single-bucket strategy?
- How do you manage object lifecycle economically?
- How do you secure PII in object storage?

---

## 1. Question
How do you design Cloud Storage layout for analytics performance and governance?

## 2. Why interviewer asks this
To evaluate practical data-lake organization maturity.

## 3. Detailed Answer
Use zone- and domain-based paths:
`gs://lake/raw/domain/entity/dt=YYYY-MM-DD/`
`gs://lake/curated/domain/entity/...`
Guidelines:
- Keep naming conventions strict.
- Avoid excessive tiny files.
- Keep schema metadata externally tracked.
- Use policy tags/classification markers for sensitive domains.

## 4. Real-world scenario
A logistics company standardized naming and partition folders across 40 pipelines, reducing onboarding and troubleshooting effort significantly.

## 5. Follow-up questions
- How do you enforce naming standards?
- How to handle late-arriving files?
- What is your compaction strategy?

---

## 1. Question
Bigtable vs BigQuery: when do you use which?

## 2. Why interviewer asks this
Mandatory storage decision test.

## 3. Detailed Answer
- **Bigtable**: low-latency, high-throughput key-value access; ideal for operational serving (time-series/user profile lookups).
- **BigQuery**: analytical SQL warehouse for scans, joins, aggregations, BI.
Use Bigtable for millisecond point/range reads; BigQuery for analytical workloads requiring complex SQL and broad scans.

## 4. Real-world scenario
A recommendation service reads user features from Bigtable in real time, while trend analysis and model training data is queried from BigQuery.

## 5. Follow-up questions
- How does Bigtable schema/row-key design affect performance?
- When should data be duplicated across both stores?
- How do you maintain consistency between serving and analytics layers?

---

## 1. Question
Explain Bigtable data model and row key design principles.

## 2. Why interviewer asks this
To test practical ability to build performant Bigtable systems.

## 3. Detailed Answer
Bigtable model:
- Sparse, distributed map indexed by row key.
- Column families contain dynamic columns.
Key design rules:
- Row key drives locality and access performance.
- Avoid hotspotting (e.g., monotonically increasing keys).
- Use salting/hash prefixes or bucketing for high write rates.
- Keep rows reasonably sized and access-pattern aligned.

## 4. Real-world scenario
IoT telemetry row keys designed as `deviceHash#reverseTimestamp` enabled balanced writes and efficient recent-history reads per device.

## 5. Follow-up questions
- How do you diagnose hotspots?
- TTL and GC policy design?
- Bigtable filters vs application-side filtering trade-offs?

---

## 1. Question
How do you model time-series data in Bigtable?

## 2. Why interviewer asks this
Common real-world design problem in telemetry and IoT.

## 3. Detailed Answer
Pattern:
- Row key includes entity + time bucketing strategy.
- Use reversed timestamp when latest-first reads dominate.
- Column qualifiers can represent metrics or dimensions.
- Tune GC policies for retention.
- Aggregate older high-granularity data into lower granularity summaries.

## 4. Real-world scenario
Fleet telemetry retained per-second granularity for 7 days and hourly aggregates for 1 year, balancing cost and query latency.

## 5. Follow-up questions
- How to prevent hot partitions during traffic spikes?
- When should you move historical series to BigQuery?
- How do you handle schema evolution in time-series fields?

---

## 1. Question
What is Cloud Composer and where does it fit in GCP pipelines?

## 2. Why interviewer asks this
To assess orchestration maturity and workflow reliability design.

## 3. Detailed Answer
Cloud Composer is managed Apache Airflow on GCP for DAG-based orchestration.
Use it to coordinate:
- batch schedules,
- cross-service dependencies,
- retries/alerts/SLAs,
- backfills and operational workflows.
Do not use it as the heavy compute engine itself; delegate compute to Dataflow/Dataproc/BigQuery jobs.

## 4. Real-world scenario
A nightly DAG orchestrates Cloud Storage ingestion validation, Dataproc ETL, BigQuery model refresh, data quality checks, and Slack incident alerts.

## 5. Follow-up questions
- Composer vs Workflows for orchestration?
- How do you manage Airflow dependency/version upgrades?
- How do you structure DAGs for multi-team ownership?

---

## 1. Question
How do you design robust Airflow DAGs in Composer?

## 2. Why interviewer asks this
To test production-grade orchestration practices.

## 3. Detailed Answer
Best practices:
- Idempotent tasks and deterministic task boundaries.
- Externalized configuration (variables/secrets/env).
- Sensor usage carefully tuned to avoid resource waste.
- Clear retry policies by failure type.
- Task groups/modular operators for maintainability.
- SLA and alerting integration with on-call systems.

## 4. Real-world scenario
A platform team split monolithic DAG into domain DAGs with standardized reusable operators, reducing MTTR and deployment risk.

## 5. Follow-up questions
- Dynamic DAG generation risks?
- Backfill strategy in Composer?
- How do you avoid task dependency spaghetti?

---

## 1. Question
How do you secure GCP data pipelines end-to-end?

## 2. Why interviewer asks this
Security and compliance are mandatory in senior interviews.

## 3. Detailed Answer
Security stack:
- IAM least privilege and service-account scoping.
- VPC Service Controls for perimeter protection.
- CMEK for regulated encryption requirements.
- Secret Manager for credentials.
- DLP/classification controls for sensitive data.
- Audit trails with Cloud Audit Logs.
- Fine-grained BigQuery access controls (policy tags, row-level security).

## 4. Real-world scenario
Healthcare analytics platform applied CMEK + VPC-SC + column-level policy tags to isolate PHI and pass compliance audits.

## 5. Follow-up questions
- How to prevent service account key sprawl?
- Policy tags vs authorized views in BigQuery?
- How do you implement cross-project secure access?

---

## 1. Question
How do you monitor and alert for GCP data pipeline health?

## 2. Why interviewer asks this
Operational excellence and incident readiness are key hiring signals.

## 3. Detailed Answer
Monitor at multiple layers:
- Ingestion rate and lag (Pub/Sub backlog, subscription metrics).
- Processing latency/error rates (Dataflow job metrics).
- Warehouse freshness and DQ checks (BigQuery).
- Orchestration failures/SLA misses (Composer).
Create severity-based alerts and runbooks:
- P1 for data loss risks.
- P2 for freshness SLA breaches.
- P3 for quality degradation trends.

## 4. Real-world scenario
A subscription backlog spike alert triggered autoscaling and incident response before downstream dashboards breached SLA.

## 5. Follow-up questions
- Which metrics are leading indicators?
- How do you reduce alert noise?
- How<create_file>
<path>data-engineer-prep/interview_preparation/gcp_interview_preparation.md</path>
<content># 🎯 GCP Data Engineer Interview Preparation (Google-Level)

**Act as Senior GCP Data Engineer with deep expertise in Google-level interviews**

Prepare for GCP Data Engineer interviews with deep conceptual clarity, system design thinking, and production reliability patterns.

---

## 📘 STRUCTURE FOR EVERY QUESTION
1. **Question**  
2. **Why interviewer asks this**  
3. **Detailed Answer**  
4. **Real-world scenario**  
5. **Follow-up questions**  

---

## 🔥 MUST COVER TOPICS
- BigQuery
- Dataflow (Apache Beam)
- Dataproc (Spark)
- Pub/Sub
- Cloud Storage
- Bigtable
- Composer (Airflow)

---

## ⚠️ COMMON MISTAKES
- **Not understanding BigQuery pricing** - Treating it as "free SQL"
- **Poor partitioning** - No clustering/partitioning causing $10K+ bills
- **Misusing Data
