# Incremental SCD2 Pipeline — Implementation Guide

## 1) End-to-End Flow
1. **Ingest** CDC/events from broker to bronze.
2. **Normalize schema** and enforce canonical datatypes.
3. **Deduplicate** by business key + event sequencing metadata.
4. **Detect changes** using `record_hash` for tracked columns.
5. **Apply SCD2 merge**:
   - close old current row (`effective_end_ts = new_start_ts - epsilon`, `is_current = false`)
   - insert new current row (`effective_start_ts = event_ts`, `effective_end_ts = 9999-12-31`, `is_current = true`)
6. **Publish metrics** to audit tables and monitoring.
7. **Checkpoint/commit** for exactly-once sink semantics with idempotent logic.

## 2) Pseudo Merge Logic
```sql
MERGE INTO dim_customer_scd2 t
USING staged_changes s
ON t.customer_id = s.customer_id
AND t.is_current = true
WHEN MATCHED AND t.record_hash <> s.record_hash THEN
  UPDATE SET
    t.effective_end_ts = s.effective_start_ts - INTERVAL 1 MICROSECOND,
    t.is_current = false,
    t.updated_at = current_timestamp()
WHEN NOT MATCHED THEN
  INSERT (
    customer_id, customer_name, tier, city, risk_score,
    record_hash, effective_start_ts, effective_end_ts, is_current,
    batch_id, ingestion_ts, source_system
  ) VALUES (
    s.customer_id, s.customer_name, s.tier, s.city, s.risk_score,
    s.record_hash, s.effective_start_ts, timestamp('9999-12-31 00:00:00'),
    true, s.batch_id, s.ingestion_ts, s.source_system
  );
```

## 3) Late Data and Corrections
- Keep a configurable watermark (e.g., 48h).
- For older corrections:
  - identify impacted timeline rows
  - split intervals where necessary
  - rebuild customer timeline deterministically for affected keys only.
- Use “repair mode” job for deep backfills.

## 4) Idempotency Strategy
- Unique event key: `event_id` or `(customer_id, event_ts, source_seq_id)`.
- Dedup state store before merge.
- Batch replay safe because merge predicates prevent duplicate current rows.
- Store `processed_batch_id` and source offsets.

## 5) Backfill Strategy
- Run batch replay over historical partitions by date range.
- Write to isolated temp table, compare row counts/hashes, then swap.
- Use table time-travel snapshots for quick rollback.

## 6) Performance Tuning
- Tune micro-batch trigger for target SLA.
- Enable AQE and skew join optimization.
- Compact small files every N batches.
- Partition pruning with date-based filters.
- Use efficient formats (Parquet + Delta/Iceberg metadata).

## 7) Failure Recovery
- Retries with exponential backoff for transient failures.
- Dead-letter queue for poison messages.
- Automatic restart from checkpoint.
- Alerting on lag, bad records, and merge conflict spikes.

## 8) Interview Questions
1. Why SCD2 over SCD1 for customer profile management?
2. How would you handle out-of-order updates for the same key?
3. What is your strategy for idempotent merge in distributed systems?
4. How do you mitigate skew in merge-heavy dimensions?
5. Trade-offs between Delta/Iceberg/Hudi for SCD2?
6. How do you test correctness for backfill replays?
7. What failure scenarios can corrupt history and how do you prevent them?
