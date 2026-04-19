# 🧱 Production Batch Data Pipelines (Azure, AWS, GCP)

## 1. Concept Explanation

A **batch pipeline** processes data in scheduled intervals (hourly/daily) with strong guarantees for completeness, reconciliation, and downstream consistency.

Production-grade batch design principles:
- **Idempotent writes** (re-runs should not duplicate data)
- **Incremental loads** (CDC/watermark instead of full reload)
- **Data quality gates** before publish
- **Layered storage** (raw/bronze/silver/gold)
- **Observable runs** (lineage, logs, metrics, alerts)
- **Backfill strategy** (historical replay with bounded blast radius)

Typical SLAs:
- T+1 daily finance reporting
- 4 AM warehouse availability
- <1% failed partition rate per month

---

## 2. Architecture Flow (Text Diagrams)

### Generic Batch Flow
```text
OLTP DB / SaaS / Files
   → Ingestion (extract/CDC/snapshot)
   → Raw Zone (immutable)
   → Transform Engine
   → Curated Zone
   → Warehouse / Serving Layer
   → BI / ML / APIs
```

### Azure Batch Flow
```text
Azure SQL / APIs / Blob
  → ADF (Copy + Metadata-driven orchestration)
  → ADLS Gen2 (raw/bronze)
  → Databricks (PySpark transformations, Delta MERGE)
  → Synapse Dedicated SQL Pool (star schema marts)
  → Power BI / downstream consumers
```

### AWS Batch Flow
```text
RDS / DynamoDB export / SaaS
  → S3 Landing
  → AWS Glue Crawlers + Glue ETL / EMR Spark
  → S3 Curated (Parquet/Delta/Hudi/Iceberg)
  → Redshift (COPY / Spectrum / MERGE patterns)
  → QuickSight / downstream jobs
```

### GCP Batch Flow
```text
Cloud SQL / GCS file drops / SaaS
  → Data Transfer / custom ingestion jobs
  → GCS Raw
  → Dataflow batch or Dataproc Spark
  → BigQuery curated datasets
  → Looker / Vertex AI features
```

---

## 3. Cloud-Specific Implementations

## Azure (ADF + ADLS + Databricks + Synapse)

### Core pattern
1. ADF pipeline reads metadata table (source/table/load_type/watermark).
2. Copy Activity lands source data in ADLS `/raw/{source}/{table}/ingest_date=YYYY-MM-DD/`.
3. Databricks notebook performs bronze-to-silver cleanup and upserts:
   - dedup by business key + latest event timestamp
   - schema evolution controls
4. Delta silver table merged into gold marts.
5. Synapse loads dimensional/fact tables with distribution keys.

### Incremental load with watermark (example)
```sql
SELECT * 
FROM sales.orders
WHERE updated_at > :last_watermark
  AND updated_at <= :current_batch_cutoff;
```

### Synapse model pattern
- `fact_orders` hash-distributed on `customer_id`
- `dim_customer` replicated (small dim)
- partition `fact_orders` by `order_date_key`

---

## AWS (S3 + Glue + EMR + Redshift)

### Core pattern
1. Source snapshot/CDC arrives in S3 landing.
2. Glue crawler/catalog updates metadata.
3. Glue job or EMR Spark transforms to partitioned Parquet.
4. Redshift COPY from curated S3.
5. MERGE for dimensions (SCD2 where needed), INSERT for facts.

### Redshift loading guardrails
- Use **manifest files** to avoid partial loads.
- Staging table + MERGE to ensure idempotency.
- VACUUM/ANALYZE or auto-table optimization.

---

## GCP (Pub/Sub + Dataflow + BigQuery for unified pipeline context)

Even in batch-focused systems, GCP teams often use Pub/Sub for ingestion buffering and Dataflow batch mode for reprocessing.

### Core pattern
1. Scheduled pull/export into GCS raw.
2. Dataflow batch transforms and validates records.
3. BigQuery partitioned tables loaded with `WRITE_APPEND`.
4. MERGE statements publish to marts.

### BigQuery MERGE idempotent pattern
```sql
MERGE analytics.fact_orders T
USING staging.fact_orders S
ON T.order_id = S.order_id
WHEN MATCHED AND S.updated_at > T.updated_at THEN
  UPDATE SET amount = S.amount, updated_at = S.updated_at
WHEN NOT MATCHED THEN
  INSERT (order_id, customer_id, amount, updated_at)
  VALUES (S.order_id, S.customer_id, S.amount, S.updated_at);
```

---

## 4. Failure Handling

Production failure controls:
- **Retry policies**
  - transient failures: exponential backoff (e.g., 1m, 5m, 15m)
  - bounded retries, then fail fast
- **Checkpointing**
  - track processed file list, watermark table, job run state
- **Dead-letter queues (DLQ)**
  - invalid payloads routed to DLQ storage/topic for triage
- **Atomic publish**
  - write to staging path/table then swap/merge
- **Poison batch isolation**
  - fail one partition, continue others where possible
- **Backfill isolation**
  - separate compute queues and target schema for replay

---

## 5. Logging & Monitoring

### Azure
- Azure Monitor + Log Analytics
- ADF pipeline run metrics (duration, failures, retries)
- Databricks job cluster metrics + structured logs
- Alert rules for SLA miss, error spikes

### AWS
- CloudWatch logs/metrics for Glue/EMR/Step Functions
- Custom metrics: records_processed, bad_records, lag_minutes
- SNS/PagerDuty for alert routing

### GCP
- Cloud Monitoring (Stackdriver) dashboards
- Dataflow worker errors + throughput metrics
- BigQuery INFORMATION_SCHEMA job observability

Golden signals:
- freshness lag
- failure rate
- throughput per partition
- cost per successful GB processed

---

## 6. Real-World Scenarios

### Uber ride settlement (daily)
- Input: ride events, payments, refunds
- Requirement: daily city-level reconciliation by 5 AM local
- Design:
  - raw append-only storage
  - idempotent dedup keys (`ride_id`, `event_version`)
  - reconciliation table with expected vs actual totals
- Outcome: reliable finance close with replay capability

### E-commerce daily orders pipeline
- Input: orders, order_items, inventory snapshots
- Requirement: T+1 business dashboards + anomaly alerts
- Design:
  - incremental CDC loads
  - partition by `order_date`
  - SCD2 customer dimension
- Outcome: stable daily reporting during peak campaigns

---

## 7. Common Mistakes

1. Full table reloads for large mutable tables.
2. No watermark persistence between runs.
3. Writing tiny files (small file problem) causing slow reads.
4. Missing idempotency; retries create duplicates.
5. Coupling ingestion and transformation in one brittle job.
6. No backfill path; ad-hoc reprocessing breaks prod.
7. Ignoring schema evolution until runtime failure.

---

## 8. Performance Tips

- Use **incremental + partition pruning** always.
- Compact small files (target 128MB–1GB file size per object).
- Prefer columnar formats (Parquet/Delta/Iceberg/Hudi).
- Push heavy joins to distributed engines (Spark/Dataflow).
- Optimize warehouse sort/distribution keys.
- Cache hot dimensions in Spark when reused.
- Tune shuffle partitions to data volume.
- Separate compute pools for ETL vs BI queries.

---

## 9. 🔥 Interview Questions (Batch Pipelines)

### Q1. What is idempotency?
**Answer:** Idempotency means rerunning the same batch with the same input produces the same final state. Implement with MERGE/upsert semantics, deterministic keys, and run metadata tracking.

### Q2. How do you handle late-arriving data?
**Answer:** Use watermark windows + correction jobs:
- keep partitions mutable for an allowed lateness window (e.g., 7 days)
- perform periodic reconciliation MERGEs
- maintain event_time-based partition logic, not ingestion-time only

### Q3. What is exactly-once processing?
**Answer:** End-to-end exactly-once means every record affects the target once, even with retries. In batch, combine deterministic dedup keys, transactional MERGE, checkpointed progress, and atomic commits.

### Q4. How do you design fault-tolerant pipelines?
**Answer:** Separate stages, persist intermediate state, add retries/backoff, isolate bad records in DLQ/quarantine, use idempotent writes, and provide replay/backfill mechanisms with observability.

### Additional interview prompts
- How do you backfill 2 years without hurting production SLA?
- When do you choose EMR vs Glue vs Redshift SQL transforms?
- How do you validate schema drift and prevent silent corruption?
- How do you calculate and enforce data freshness SLAs?
