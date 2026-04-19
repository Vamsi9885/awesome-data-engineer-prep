# Log Analytics Platform — Architecture

## Text-Based Architecture Diagram
```text
[Apps / API Gateways / Infra Agents / Audit Systems]
                     |
                     v
             [Kafka / Event Hubs]
                     |
                     v
          [Bronze Raw Log Lake (S3/ADLS/GCS)]
                     |
                     v
        [Spark Streaming Parse + Normalize + DQ]
          |                |                 |
          v                v                 v
   [DLQ invalid]   [Dedup + Watermark] [PII masking]
          \                |                /
           \               v               /
                    [Silver Curated Logs]
                             |
          +------------------+------------------+
          |                                     |
          v                                     v
 [Search Index (OpenSearch/Elastic)]     [Gold Analytics Tables]
          |                                     |
          v                                     v
 [Incident Dashboards + Alerting]     [BI, SLO Reports, Security Analytics]
```

## Cloud Service Justification
- **Kafka/Event Hubs:** high-throughput ordered ingestion with replay.
- **Object storage:** low-cost durable log retention + backfill source.
- **Spark Structured Streaming:** schema handling, dedup, watermarking, enrichment.
- **OpenSearch/Elasticsearch:** fast full-text search for troubleshooting.
- **Lakehouse tables (Delta/Iceberg):** ACID analytics and incremental updates.
- **Airflow/Composer:** orchestration for compaction, retention, and quality jobs.
- **Monitoring stack:** pipeline lag, error rates, and alert reliability.

## Reliability Strategy
- At-least-once ingestion + deterministic dedup key (`event_id`).
- Checkpointing for stream recovery.
- Retry with exponential backoff for sink writes.
- DLQ for malformed records with replay workflow.
- Exactly-once effect in gold via idempotent merge/upsert.

## Real-World Challenges + Handling
- **Skew:** shard heavy services by hash salt.
- **Late logs:** 30-minute watermark and correction window.
- **Duplicates:** event-id + payload hash dedup.
- **Schema evolution:** permissive parse + schema registry compatibility checks.
- **Backfill:** date-partition replay into isolated tables then swap.

## Performance and Scaling
- Partition silver/gold by `event_date`, `service_name`.
- Cache hot aggregates for dashboards.
- Autoscale streaming workers by lag and throughput.
- Compact small files; use Parquet/Delta compression.
- Tiered retention: hot(7d), warm(30d), cold(365d+).

## Failure Recovery and Idempotency
- Resume from checkpoints.
- Re-run partitions idempotently by deterministic keys.
- Snapshot rollback for bad deployments.
- Alert on lag, parse failures, indexing failures, and SLA breaches.

## Interview Questions
1. Search index vs lakehouse for log analytics—when to use each?
2. How do watermark settings impact late data correctness?
3. How to design dedup when event IDs are missing?
4. What causes skew in log pipelines and how do you fix it?
5. How would you control storage cost without losing incident value?
6. How do you prove idempotency in replay scenarios?
