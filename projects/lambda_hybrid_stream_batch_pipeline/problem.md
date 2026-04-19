# Lambda Hybrid Stream-Batch Pipeline — Problem Statement

## Business Context
A digital marketplace needs both real-time operational metrics (seconds) and highly accurate historical analytics (hours) for revenue, engagement, and fraud monitoring. A single processing path cannot satisfy both latency and correctness.

## Functional Requirements
- Build Lambda architecture with:
  - Speed layer (streaming, low latency)
  - Batch layer (accurate recomputation)
  - Serving layer (unified query interface)
- Handle late/out-of-order events.
- Reconcile stream outputs with batch-corrected results.
- Support reprocessing/backfill for historical corrections.

## Non-Functional Requirements
- Real-time latency < 10 seconds for speed KPIs.
- Batch correctness refresh every 2 hours.
- 99.9% reliability and idempotent processing.
- Cost-efficient scaling for peak events.

## Challenges
- Duplicates and replay in stream ingestion.
- Skew on celebrity sellers/high-traffic categories.
- Schema evolution in event payloads.
- Consistency drift between speed and batch outputs.

## Success Criteria
- Streaming and batch reconciliation gap < 0.5%.
- Critical dashboard freshness and accuracy SLAs met.
