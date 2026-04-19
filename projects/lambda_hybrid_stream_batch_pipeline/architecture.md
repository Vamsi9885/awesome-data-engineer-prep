# Lambda Hybrid Stream-Batch Pipeline — Architecture

## Text-Based Diagram
```text
             [Event Producers]
                    |
                    v
              [Kafka/Event Hub]
               /             \
              /               \
             v                 v
   [Speed Layer - Streaming]  [Batch Layer - Data Lake]
   (Spark/Flink low-latency)    (hourly recompute jobs)
             |                 |
             v                 v
   [Speed Serving Table]   [Batch Serving Table]
              \               /
               \             /
                v           v
                [Reconciliation Layer]
                        |
                        v
                [Unified Serving API/BI]
```

## Service Justification
- Stream engine for low-latency KPIs.
- Batch engine for complete and corrected aggregates.
- Lakehouse storage for ACID merge and historical replay.
- Serving layer combines speed and batch views with precedence rules.

## Reliability Strategy
- Checkpointing in stream path.
- Idempotent stream upserts keyed by event_id.
- Batch snapshots with replay/backfill support.
- Reconciliation job aligns speed with batch truth.
- Retry and DLQ for ingestion failures.

## Real-World Challenges
- **Skew:** high-volume users cause hotspot partitions.
- **Late events:** stream watermark and batch correction.
- **Duplicates:** dedup by event_id.
- **Schema evolution:** contract checks and compatibility mode.
- **Backfill:** batch replay updates serving history.

## Performance and Scaling
- Partition by event_date/hour.
- Autoscale stream consumers on lag.
- Cache serving aggregates.
- Compact files from both paths.
- Optimize joins using broadcast and AQE.

## Recovery and Idempotency
- Resume stream from checkpoint offsets.
- Batch rerun by partition window.
- Deterministic merge in serving tables.

## Interview Questions
1. Why Lambda vs Kappa architecture?
2. How do you reconcile stream and batch outputs?
3. How do you prevent double counting?
4. What happens during prolonged stream outage?
5. How to tune watermark and backfill windows?
