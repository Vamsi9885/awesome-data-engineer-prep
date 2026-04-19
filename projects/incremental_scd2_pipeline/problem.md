# Incremental SCD2 Pipeline — Problem Statement

## Business Context
A retail enterprise maintains customer profile attributes (tier, address, segment, risk score) across CRM, loyalty, and support systems. Analysts need **historical point-in-time accuracy** for customer behavior studies, churn models, and regulatory audits. Current overwrite-based ETL loses history and creates reporting inconsistencies.

The business needs a production-grade **incremental SCD Type 2 pipeline** that tracks every dimension change with effective time windows and supports low-latency updates.

## Objectives
1. Build a resilient incremental ingestion pattern for customer dimension updates.
2. Implement SCD2 merge logic preserving complete history.
3. Enable backfills and late-arriving corrections without corrupting timelines.
4. Support analytics queries for “as-of” reporting.

## Functional Requirements
- Ingest daily and intraday customer change feeds from CDC snapshots and event logs.
- Detect changed records using hash diff and business keys.
- Manage SCD2 columns:
  - `effective_start_ts`
  - `effective_end_ts`
  - `is_current`
  - `record_hash`
- Close previous active record and insert new version on changes.
- Ignore exact duplicates idempotently.
- Handle out-of-order (late) updates with timeline correction logic.
- Provide gold dimension table for downstream marts.
- Emit data quality metrics and reconciliation reports.

## Non-Functional Requirements
- **Scalability:** 200M customer versions, 10M daily changes.
- **Latency:** < 15 minutes micro-batch freshness.
- **Reliability:** 99.9% successful daily runs.
- **Idempotency:** Safe reruns without duplicate versions.
- **Auditability:** Full lineage and per-batch checkpoints.
- **Cost efficiency:** Partition pruning, compaction, optimized file formats.

## Inputs and Outputs
### Input
- CDC file stream (Parquet/JSON) in object storage.
- Change events (`upsert`, `delete`, `correction`) from Kafka/Event Hubs/PubSub.

### Output
- `dim_customer_scd2` (gold table, Delta/Iceberg/Hudi).
- Operational audit tables (`batch_metrics`, `dq_failures`, `merge_stats`).

## Real-World Data Challenges
- Key skew on high-activity enterprise customers.
- Duplicate events from retries.
- Schema evolution (new optional attributes).
- Late and backfilled records with older event timestamps.
- Null-heavy attributes and source-system conflicts.

## Success Criteria
- Point-in-time query parity with source-of-truth audit samples > 99.95%.
- Duplicate update amplification < 0.1%.
- Backfill correctness validated on 12-month replay window.
