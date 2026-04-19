# Log Analytics Platform — Implementation

## End-to-End Implementation Flow
1. Collect logs from Fluent Bit/Vector agents and app emitters.
2. Publish to Kafka/Event Hubs with topic partitioning by `service_name`.
3. Spark streaming job reads, parses, and validates records.
4. Route invalid payloads to DLQ.
5. Deduplicate and apply watermark handling for late events.
6. Write curated silver tables (Delta/Iceberg).
7. Build gold aggregates for error rate, latency, traffic, and security incidents.
8. Index selected fields to OpenSearch for low-latency text search.
9. Run scheduled compaction/retention jobs.

## Reliability and Recovery
- Checkpoint every micro-batch.
- Retry sink writes with exponential backoff.
- Idempotent upsert using event IDs.
- DLQ replay job for corrected malformed logs.
- Table snapshot rollback for bad deployments.

## Data Quality Rules
- Required: `timestamp`, `service_name`, `severity`, `message`.
- Validate timestamp parse and accepted severity enum.
- Drop or quarantine oversized malformed entries.
- Track parse success rate, null ratios, and source drift.

## Handling Challenges
- **Skew:** split high-volume services via virtual shards.
- **Late events:** watermark + bounded correction process.
- **Duplicates:** event fingerprint hash + stateful dedup.
- **Schema evolution:** permissive mode + contract tests.
- **Backfill:** date-range replay to temporary tables then merge.

## Performance Strategy
- Partition by `event_date`, `service_name`.
- Use column pruning and predicate pushdown in Parquet/Delta.
- Cache top N service aggregates for dashboards.
- Auto-scale streaming executors on lag.
- Tiered storage for hot/warm/cold logs.

## Interview Questions
1. How would you balance search latency vs storage cost?
2. What dimensions drive partition strategy in logs?
3. How to tune watermark for correctness vs latency?
4. How to prevent duplicate alert storms?
5. How do you evolve schema without breaking consumers?
