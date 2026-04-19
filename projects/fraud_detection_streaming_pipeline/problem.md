# Fraud Detection Streaming Pipeline — Problem Statement

## Business Context
A fintech platform processes card transactions globally and must detect fraudulent behavior in near real time to reduce chargebacks and compliance risk.

## Functional Requirements
- Ingest transaction events continuously.
- Compute real-time fraud features (velocity, geo anomaly, device mismatch).
- Score transactions using rule engine + ML score.
- Route high-risk events for hold/review.
- Persist decisions and features for audit and model retraining.

## Non-Functional Requirements
- Detection latency < 2 seconds.
- 99.95% pipeline availability.
- Idempotent replay handling for duplicate events.
- Explainable rules for compliance audit.
- Scalable to peak bursts (10x normal TPS).

## Challenges
- Event duplication and retries.
- Late/out-of-order auth/settlement events.
- Heavy skew for high-volume merchants/cards.
- Schema evolution from payment gateways.
- Balancing false positives vs missed fraud.

## Success Criteria
- Fraud loss reduction target met quarter-over-quarter.
- Precision/recall thresholds maintained.
- End-to-end traceability for all blocked transactions.
