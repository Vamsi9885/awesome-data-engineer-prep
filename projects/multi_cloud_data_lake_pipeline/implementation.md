# Implementation — Multi-Cloud Data Lake Pipeline

## 1) End-to-End Pipeline Flow

1. **Ingestion orchestration**
   - Trigger hourly ingestion DAG with cloud-specific tasks.
   - Parameterize by `run_id`, `run_date`, `source_cloud`, `dataset`.

2. **Raw to Bronze**
   - Read source files/events from S3/ADLS/GCS.
   - Append to bronze Delta tables with immutable metadata columns:
     - `source_cloud`, `source_path`, `ingest_ts`, `run_id`, `record_hash`.

3. **Bronze to Silver (canonicalization)**
   - Enforce schema contracts.
   - Standardize:
     - currency to USD
     - timestamps to UTC
     - country codes to ISO standard
   - Deduplicate by business key + latest event time.
   - Quarantine invalid rows.

4. **Silver to Gold**
   - Build marts:
     - `fact_orders_global`
     - `fact_payments_global`
     - `dim_customer_scd2`
     - `agg_daily_revenue_country`
   - Use incremental merge patterns by partition.

5. **Publish to serving layers**
   - Export curated outputs to Snowflake and BigQuery.
   - Run reconciliation checks for key aggregates.

6. **Observability and control**
   - Emit pipeline metrics:
     - ingest lag
     - duplicate rate
     - null-rate drift
     - per-task cost estimate

---

## 2) Data Transformations

## Canonical schema strategy

Example canonical order schema:
- `order_id STRING`
- `customer_id STRING`
- `country_code STRING`
- `order_ts_utc TIMESTAMP`
- `order_amount_usd DECIMAL(18,2)`
- `currency_code STRING`
- `event_version INT`
- `source_cloud STRING`
- `event_date DATE`

Transformation rules:
- parse nested JSON payloads into flattened structures
- normalize decimal precision for money columns
- enforce deterministic `record_hash = sha2(concat_ws('||', ...), 256)`

---

## Deduplication and late data handling

1. Watermark strategy:
   - accept late events up to 72 hours for orders/payments
2. Dedup key:
   - (`order_id`, `event_version`) preferred
   - fallback to (`order_id`, `record_hash`)
3. Use `ROW_NUMBER()` window over key ordered by `event_ts desc, ingest_ts desc`
4. Keep `row_number = 1`

---

## SCD Type 2 (customer dimension)

- Identify changes using hash of tracked attributes.
- Close previous record (`is_current = false`, `effective_to = new_effective_from - interval 1 second`).
- Insert new version row with `is_current = true`.

---

## 3) Storage Strategy

### Bronze
- immutable append-only Delta
- retention 45 days for replay convenience

### Silver
- conformed curated Delta
- retention 180 days + VACUUM policy

### Gold
- business-ready Delta marts
- optimized for BI query patterns

File-format decisions:
- Delta for transactional reliability
- Parquet underneath for efficient columnar scans
- periodic compaction to reduce small files

---

## 4) Partitioning and Performance

- Bronze: `ingest_date`, `source_cloud`
- Silver facts: `event_date`, `country_code`
- Gold aggregates: `ds`, `country_code`

Performance controls:
- autoscaling clusters with spot + on-demand fallback
- AQE enabled
- broadcast small dimensions
- cache hot intermediate dimensions
- run `OPTIMIZE` for frequently queried tables

---

## 5) Fault Tolerance and Idempotency

- each run isolated by `run_id`
- writes are transactional via Delta
- re-running same `run_id` does not duplicate outputs
- failed tasks retried with exponential backoff
- dead-letter table stores malformed/contract-breaking records

Mid-run failure recovery:
1. detect failed partition ranges from control table
2. delete/rebuild only impacted partitions in silver/gold
3. validate row counts and checksums before publishing

---

## 6) Data Quality and Validation

Validation checks:
- not-null (`order_id`, `customer_id`, `order_ts_utc`)
- uniqueness (`order_id`, `event_version`) in silver
- referential checks (`customer_id` exists in dim)
- accepted value checks (`country_code` in ISO list)

Reconciliation checks:
- source vs silver count variance threshold <= 0.2%
- source vs gold amount variance threshold <= 0.1%

---

## 7) Backfill Strategy

- backfill tool accepts:
  - `start_date`
  - `end_date`
  - `datasets`
  - `priority`
- uses same production code path (no special-case scripts)
- isolates backfill compute queues from real-time SLA jobs
- reconciles before promoting backfill outputs as authoritative

---

## 8) Common Mistakes and How This Design Avoids Them

- Tight coupling across clouds → avoided via canonical contracts + decoupled ingestion tasks
- No retry logic → explicit retries with bounded backoff
- No idempotency → deterministic keys + merge semantics
- Poor partitioning → partition design by temporal and regional access patterns

---

## 9) Scaling to 10x

If event volume increases 10x:
1. move ingestion to continuous autoloader mode for high-throughput sources
2. shard largest country partitions with salting strategy
3. add tiered gold tables (hot weekly + cold historical)
4. push heavy joins to pre-aggregated feature tables
5. enforce stricter file size compaction cadence

---

## Interview Questions (Implementation Focus)

### Conceptual
1. Why is one canonical schema layer better than direct per-cloud mart pipelines?

### Trade-offs
2. Why use merge-based upsert vs append + periodic dedupe?

### Scaling
3. Which operations are most expensive at 10x and how do you redesign them?

### Failure Scenarios
4. How do you guarantee no duplicates after rerunning a failed partition?

### Optimization
5. How do you optimize between low latency and low compute cost?
