# Cross-Cloud Data Migration Pipeline — Implementation

## End-to-End Steps
1. Inventory source datasets and generate migration manifest.
2. Run initial bulk copy by partition/date buckets.
3. Start CDC pipeline for ongoing changes.
4. Normalize schema and map types at target.
5. Validate row counts, min/max timestamps, and checksum hashes.
6. Reconcile mismatches and replay failed chunks.
7. Enable dual-write/dual-read validation window.
8. Execute controlled cutover and monitor post-cutover health.

## Reliability Strategy
- Checkpoint transfer status per dataset/partition.
- CDC offset tracking per source stream.
- Idempotent merge into target.
- Retry with exponential backoff for network/transient failures.
- Quarantine malformed records for manual triage.

## Handling Challenges
- **Skewed partitions:** split oversized partitions into sub-chunks.
- **Late data:** keep pre-cutover overlap replay window.
- **Duplicates:** event sequence + hash-based dedup.
- **Schema evolution:** compatibility matrix and transform adapters.
- **Backfill:** rerun historical windows to temporary staging then merge.

## Security & Compliance
- TLS in transit, KMS-managed encryption at rest.
- PII masking/tokenization before target landing where required.
- Audit logs for every transfer/reconciliation step.
- Least-privilege IAM for migration workers.

## Interview Questions
1. How do you design migration cutover with rollback?
2. What validations are mandatory before promoting target?
3. How do you ensure idempotency across retries?
4. What are common cross-cloud migration bottlenecks?
5. How do you keep business continuity during long migrations?
