# Fraud Detection Streaming Pipeline — Architecture

## Text Diagram
```text
[Payment Gateways] -> [Kafka/Event Hub] -> [Stream Processor]
                                          |      |
                                          |      v
                                          | [Feature Store Online]
                                          v
                                  [Rule + ML Scoring Service]
                                          |
                         +----------------+----------------+
                         |                                 |
                         v                                 v
                 [Approve / Continue]            [Hold / Review Queue]
                         |
                         v
              [Fraud Decisions + Audit Lakehouse]
                         |
                         v
                [Monitoring + Model Retraining]
```

## Service Justification
- Streaming bus for durable event ingestion.
- Stream processor for low-latency feature computation.
- Online feature store for millisecond reads.
- Rule engine + ML endpoint for hybrid explainable scoring.
- Lakehouse for immutable audit trail and retraining datasets.

## Reliability Strategy
- Checkpoint offsets in stream processor.
- Idempotent decision writes keyed by transaction_id.
- DLQ for malformed or timed-out scoring requests.
- Retry policy with bounded attempts.
- Fallback rules if ML endpoint unavailable.

## Real-World Challenges
- Skew on large merchants/cards.
- Late settlement events requiring decision reconciliation.
- Duplicate auth events and retries.
- Schema evolution from payment providers.
- Backfill historical labels for model retraining.

## Performance/Scaling
- Partition stream by card_hash and merchant_id.
- Autoscale consumers on lag and throughput.
- Cache model artifacts/features.
- Compact cold audit data by date.

## Recovery and Idempotency
- Resume from checkpoints.
- Replay from retained topic windows.
- Deterministic merge of decision records.

## Interview Questions
1. How do rules and ML scores combine safely?
2. How do you keep latency low under traffic spikes?
3. How do you handle model endpoint outages?
4. How do you tune false positive/false negative trade-offs?
5. How do you guarantee auditability for blocked payments?
