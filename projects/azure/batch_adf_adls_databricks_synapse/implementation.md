# Implementation — Azure End-to-End Batch Pipeline (ADF + ADLS + Databricks + Synapse)

## 1) End-to-End Pipeline Flow

### Step A: Orchestration (ADF)
- Trigger: daily schedule at 01:00 AM UTC.
- Pipeline parameters: `run_date`, `start_date`, `end_date`, `is_backfill`.
- Activities:
  1. Extract incremental Azure SQL data using watermark columns.
  2. Pull partner refunds API in paginated batches with checkpoint token.
  3. Copy inventory CSV drops from Blob container.
  4. Land each feed in ADLS raw with metadata (`run_id`, `ingest_ts`, `source`).

### Step B: Bronze (Databricks)
- Read raw data as append-only.
- Standardize column names and types.
- Add ingestion metadata columns.
- Deduplicate with deterministic row_number strategy on natural keys + latest update timestamp.
- Persist to Delta bronze tables partitioned by `ingest_date`.

### Step C: Silver
- Apply business quality rules:
  - non-null checks on critical keys,
  - amount/range constraints,
  - referential checks between orders and customers.
- Route invalid records to quarantine tables.
- Build conformed entities for orders, payments, refunds, and inventory.
- Handle schema evolution using add-only defaults and compatibility checks.

### Step D: Gold
- Build dimensions and facts:
  - `dim_customer` (SCD2 via Delta MERGE)
  - `dim_product`
  - `fact_orders`
  - `fact_payments`
- Aggregate and enrich for BI consumption.
- Use deterministic MERGE for idempotent reruns.

### Step E: Synapse Publish
- Stage gold partitions to Synapse external/staging tables.
- Upsert/overwrite target partition slices in dedicated SQL pool.
- Validate counts and financial totals post-load.
- Mark run successful only after reconciliation passes.

---

## 2) Reliability and Idempotency Strategy

- **Run ledger table** tracks each step status (`started/success/failed`).
- **Idempotent date-window processing** using `run_date` and merge conditions.
- **Retry with exponential backoff** in ADF and Databricks tasks.
- **Checkpointed API pulls** to avoid duplicate pages.
- **Partition reruns** without full pipeline restart.
- **Exactly-once-like semantics** using Delta transaction log + deterministic keys.

---

## 3) Late Data, Duplicates, Backfill, Schema Evolution

- **Late data:** rolling N-day correction window updates prior partitions.
- **Duplicates:** bronze dedup and gold merge key enforcement.
- **Backfill:** parameterized ADF triggers for historical date ranges (24 months).
- **Schema evolution:** controlled schema changes, defaulting, and compatibility audit logs.

---

## 4) Performance and Scaling

- Data partitioning:
  - raw/bronze by `ingest_date`
  - silver/gold facts by `business_date,country`
- Adaptive query execution in Databricks.
- ZORDER on high-selectivity columns (`order_id`, `customer_id`).
- Autoscaling job clusters for variable loads.
- Small-file compaction to reduce read overhead.
- Synapse workload groups to isolate dashboard queries.

---

## 5) Failure Recovery Playbook

1. Identify failed stage from run ledger.
2. Re-run only failed partition/date with same run parameters.
3. Validate bronze→silver→gold row deltas.
4. Re-publish impacted Synapse partitions.
5. Close incident only after reconciliation and SLA checks pass.

---

## 6) Operational Monitoring

- ADF pipeline success/failure and duration alerts.
- Databricks job SLA and cluster-cost telemetry.
- Data quality metrics (duplicate ratio, null rates, reconciliation variance).
- Gold readiness checkpoint before 06:30 AM UTC deadline.

---

## 7) Interview Questions

1. How does this design guarantee idempotent reruns for historical backfills?
2. How would you optimize cost if inventory volume doubles?
3. How do you choose partition columns for Synapse-facing facts?
4. What changes if partner API starts sending nested JSON with frequent drift?
5. How do you defend SLA under source delay + skewed country spikes?
