# Incremental SCD2 Pipeline — Architecture

## High-Level Architecture (Text Diagram)

```text
[Source Systems: CRM, Loyalty, Support]
                |
                v
     [CDC Extract / Event Streams]
      (Kafka/Event Hubs/PubSub)
                |
                v
      [Landing/Bronze Storage]
    (S3/ADLS/GCS, raw parquet/json)
                |
                v
   [Streaming + Micro-batch Engine]
         (Spark Structured Streaming)
                |
      +---------+-----------+
      |                     |
      v                     v
[Data Quality + Rules]   [Dedup + Ordering]
      |                     |
      +----------+----------+
                 v
        [SCD2 Merge Processor]
    (Delta/Iceberg/Hudi MERGE logic)
                 |
       +---------+----------+
       |                    |
       v                    v
[Gold dim_customer_scd2] [Audit Tables]
                 |
                 v
      [BI / Feature Store / APIs]
```

## Service Justification
- **Object Storage (S3/ADLS/GCS):** Durable low-cost historical landing zone; supports replay and backfill.
- **Kafka/Event Hubs/PubSub:** Scalable ingestion for near-real-time CDC events.
- **Spark Structured Streaming:** Unified batch/stream transforms, watermarking, stateful dedup.
- **Delta/Iceberg/Hudi:** ACID tables + MERGE semantics required for robust SCD2 history.
- **Orchestrator (Airflow/Composer/ADF):** Dependency management, retries, SLA notifications.
- **Monitoring stack (CloudWatch/Log Analytics/Stackdriver):** Pipeline health, lag, data quality metrics.

## Data Model
### Business Key
- `customer_id`

### SCD2 Technical Columns
- `record_hash` (hash of tracked attributes)
- `effective_start_ts`
- `effective_end_ts` (`9999-12-31` for current)
- `is_current`
- `batch_id`
- `ingestion_ts`
- `source_system`

## End-to-End Reliability Strategy
1. **At-least-once ingestion** + deterministic dedup by `(customer_id, event_ts, op_type, source_seq_id)`.
2. **Checkpointing** in streaming engine to resume after failure.
3. **Idempotent merge** using unique merge keys and hash compare.
4. **Atomic commits** in table format prevent partial writes.
5. **Retry policy** with exponential backoff for transient read/write errors.
6. **Dead-letter queue** for malformed records with triage workflow.

## Handling Real-World Challenges
- **Skew:** Salt keys for hotspot customers, AQE skew join handling.
- **Late data:** Watermark + correction workflow to reopen/close validity ranges.
- **Duplicates:** Stateful dedup + unique event IDs.
- **Schema evolution:** Additive column evolution with default/null-safe handling.
- **Backfill:** Batch replay mode with deterministic merge semantics and isolated run IDs.

## Performance and Scaling
- Partition table by `is_current` and derived date buckets from `effective_start_ts`.
- Z-order / clustering by `customer_id`.
- Periodic file compaction and optimize/vacuum routines.
- Autoscaling executors based on input lag and throughput.
- Broadcast joins for small reference data.
- Cache current-active dimension snapshot in memory for frequent lookups.

## Security and Governance
- Encryption at rest and in transit.
- Fine-grained IAM on bronze/silver/gold layers.
- Lineage capture from source event to dimension version.
- PII masking/tokenization for non-privileged consumers.

## Failure Recovery
- Restart from checkpoints.
- Reprocess by `batch_id` safely (idempotent merge).
- Rollback to previous table snapshot/time-travel if bad deployment.
