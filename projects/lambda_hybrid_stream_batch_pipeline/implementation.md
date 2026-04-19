# Lambda Hybrid Stream-Batch Pipeline — Implementation

## Implementation Flow
1. Ingest events into Kafka with schema registry contracts.
2. Speed layer computes rolling metrics (5s/1m windows).
3. Batch layer ingests immutable events to lake and recomputes accurate aggregates hourly.
4. Reconciliation job compares speed vs batch and applies corrections.
5. Serving layer exposes unified metrics with precedence:
   - Use speed for freshest interval.
   - Replace with batch once available.
6. Persist monitoring metrics (lag, drop rate, mismatch rate).

## Reliability Strategy
- Stream checkpointing and exactly-once sinks.
- Batch partition-level reruns with deterministic outputs.
- DLQ for poison messages.
- Retry policy with exponential backoff.
- Idempotent key-based MERGE in serving tables.

## Handling Real-World Challenges
- **Skew:** salting keys + adaptive execution.
- **Late data:** watermark + side outputs for correction.
- **Duplicates:** event_id dedup in both paths.
- **Schema evolution:** backward-compatible schema governance.
- **Backfill:** replay historical partitions, then reconcile.

## Performance/Scaling
- Autoscale consumers by lag threshold.
- Partition data by event_date/hour.
- Use columnar formats and compaction.
- Cache hot serving tables.
- Limit state-store growth in streaming jobs.

## Interview Questions
1. How do you decide speed/batch merge precedence?
2. How would you debug persistent reconciliation drift?
3. How do you tune stream state and watermark?
4. What failure modes break Lambda consistency?
5. When would Kappa be preferable?
