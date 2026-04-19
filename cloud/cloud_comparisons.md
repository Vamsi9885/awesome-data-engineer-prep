# Cross-Cloud Data Engineering Comparisons

## 1) ADF vs Airflow

| Dimension | Azure Data Factory | Apache Airflow (Composer/MWAA/self-managed) |
|---|---|---|
| Core strength | Managed integration/orchestration with connectors | Code-first orchestration flexibility |
| Best for | Enterprise ingestion, hybrid integration | Complex DAG logic, custom workflows |
| Skill profile | UI + parameterized pipelines | Python/DAG engineering |
| Tradeoff | Less code flexibility | More ops/engineering discipline |

**Interview angle:**  
Use ADF where connector-heavy Azure-native orchestration dominates.  
Use Airflow where workflow logic complexity and portability matter more.

---

## 2) Databricks vs EMR vs Dataproc

| Dimension | Databricks | EMR | Dataproc |
|---|---|---|---|
| Positioning | Productivity + lakehouse | Deep AWS cluster control | GCP managed Spark/Hadoop |
| Best for | Unified lakehouse ETL/ML | Custom Spark at scale on AWS | Spark pipelines on GCP with low overhead |
| Governance | Unity Catalog | IAM + Glue/Lake Formation | IAM + GCP controls |
| Typical choice driver | Team speed and platform features | Cost/control with strong Spark ops | GCP-native simplicity |

**Interview angle:**  
- Databricks for fastest platform velocity.  
- EMR/Dataproc when infra control and cost engineering are top priorities.

---

## 3) BigQuery vs Redshift vs Snowflake

| Dimension | BigQuery | Redshift | Snowflake |
|---|---|---|---|
| Model | Serverless warehouse | Managed MPP warehouse | Cloud data platform (multi-cloud) |
| Ops burden | Lowest | Medium | Low-medium |
| Cost model | Scan/slot-based | Cluster/storage based | Compute warehouse + storage |
| Best for | SQL-at-scale with minimal ops | AWS-centric heavy BI | Multi-cloud + data sharing |

**Interview angle:**  
- BigQuery: fastest to operate.  
- Redshift: strong AWS-native warehouse control.  
- Snowflake: cross-cloud strategy and sharing ecosystem.

---

## 4) S3 vs ADLS vs GCS

| Dimension | S3 | ADLS Gen2 | GCS |
|---|---|---|---|
| Ecosystem fit | AWS | Azure | GCP |
| Data lake role | Primary lake store | Primary lake store | Primary lake store |
| Governance style | IAM/Lake Formation | RBAC/ACL + Azure governance | IAM + GCP controls |
| Key note | Mature ecosystem | Enterprise ACL + Azure analytics integration | Strong BigQuery integration |

**Interview angle:**  
All three are object stores; selection is usually ecosystem/governance/tooling driven.

---

## 5) Kinesis vs Event Hubs vs Pub/Sub

| Dimension | Kinesis | Event Hubs | Pub/Sub |
|---|---|---|---|
| Cloud | AWS | Azure | GCP |
| Typical use | Stream ingest + processing | Stream ingest + Kafka compatibility | Global async messaging/stream ingress |
| Consumer model | Shards + consumers | Partitions + consumer groups | Pull/push subscriptions |
| Best with | Lambda/Flink/EMR | ASA/Databricks/Synapse | Dataflow/Functions/BigQuery |

**Interview angle:**  
Cloud-native integration often decides choice more than pure feature differences.

---

## 6) Required Real-World Architectures

### A) Batch Pipeline (Azure)
`ADF → ADLS → Databricks → Synapse`

**Why this works**
- ADF schedules and orchestrates
- ADLS stores medallion layers
- Databricks performs heavy Spark transformations
- Synapse serves BI/reporting

### B) Streaming Pipeline (AWS)
`Kinesis → Lambda → S3 → Athena`

**Why this works**
- Kinesis handles ingest bursts
- Lambda performs lightweight stream enrichment
- S3 persists raw + curated events
- Athena offers fast ad hoc/near-real-time querying

### C) Real-Time Pipeline (GCP)
`Pub/Sub → Dataflow → BigQuery`

**Why this works**
- Pub/Sub decouples producers and consumers
- Dataflow handles event-time processing/windowing
- BigQuery serves low-ops analytical consumption

---

## 7) Common Cross-Cloud Mistakes

1. Choosing services by hype, not workload pattern
2. Ignoring cost model (scan-based vs cluster-based vs serverless execution)
3. Tight coupling across services without clear contracts
4. Poor partitioning/file layout in lake storage
5. No replay/error handling strategy in streaming designs
6. No governance model across environments

---

## 8) Performance & Cost Optimization Playbook

### Partitioning Strategies
- Partition by dominant filter fields (`dt`, `region`, `tenant`)
- Avoid over-partitioning that creates tiny files

### Storage Tiering
- Hot/cool/archive lifecycle policies on S3/ADLS/GCS
- Retain raw forever only if compliance requires it

### Query Optimization
- Columnar formats (Parquet/ORC/Delta)
- Enforce selective predicate filters
- Pre-aggregate high-demand metrics with materialized views

### Auto-Scaling Compute
- Use autoscaling in Spark platforms and streaming processors
- Prefer ephemeral job clusters for batch workloads
- Right-size concurrency and workload classes in warehouses

---

## 9) High-Value Interview Drills

1. ADF vs Airflow for a 500-table enterprise migration—what drives decision?
2. Databricks vs EMR vs Dataproc under strict cost cap and 4-hour SLA.
3. BigQuery vs Redshift vs Snowflake for global SaaS analytics platform.
4. Design a replay-safe streaming architecture for order events across clouds.
5. How to migrate S3-based lakehouse to ADLS or GCS with minimal downtime?
6. Which service choices change when team skill is SQL-heavy vs Spark-heavy?
