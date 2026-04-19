# Fraud Detection Streaming Pipeline — Implementation

## End-to-End Flow
1. Ingest auth/transaction events from payment gateways.
2. Parse and validate schema; route invalid records to DLQ.
3. Compute streaming features:
   - txn velocity in 1m/5m windows
   - distance from last known geo
   - device/IP novelty score
4. Apply deterministic fraud rules.
5. Call ML scoring service for probabilistic risk score.
6. Combine rule + ML score into final decision.
7. Publish decision for transaction orchestration (approve/hold).
8. Persist all features and decisions for audit and retraining.

## Reliability Strategy
- Stream checkpointing for exactly-once recovery semantics.
- Idempotent writes by `transaction_id`.
- Retry and timeout controls around model scoring.
- Fallback safe-rule mode if model unavailable.
- DLQ + alerting for sustained parsing/scoring failures.

## Real-World Challenge Handling
- **Skew:** partition by hashed card and merchant.
- **Late events:** hold short window for settlement reconciliation.
- **Duplicates:** dedup on (`transaction_id`, `event_type`).
- **Schema evolution:** contract versioning and compatibility checks.
- **Backfill:** replay historical events with decision-version tagging.

## Performance/Scaling
- Autoscale consumers by lag and TPS.
- Cache hot features in online store.
- Use columnar compaction in audit lake.
- Separate low-latency and heavy analytics workloads.

## Interview Questions
1. How do you combine deterministic rules with ML safely?
2. How do you minimize fraud latency while controlling costs?
3. How do you recover from model-service outages?
4. How do you evaluate and reduce false positives?
5. What data do you store for regulatory investigations?
