# Cross-Cloud Data Migration Pipeline — Architecture

## Text Diagram
```text
[Source Cloud Storage + Warehouse + CDC Streams]
                    |
                    v
       [Extraction + Manifest Generator]
                    |
                    v
        [Transfer Service / Replication Bus]
     (encrypted transfer, chunked, resumable)
                    |
                    v
         [Target Cloud Landing (Bronze)]
                    |
      +-------------+-------------+
      |                           |
      v                           v
[Validation Engine]         [Schema Mapper]
(row count/hash/checksum)     (type mapping)
      |                           |
      +-------------+-------------+
                    v
           [Curated/Silver + Gold]
                    |
                    v
          [Cutover Orchestrator]
     (dual-write window + switchover)
```

## Cloud Service Justification
- Native transfer service for large-scale secure cross-cloud copy.
- Message queue/stream for CDC change propagation.
- Spark/Beam/Dataflow for transform + validation.
- Lakehouse table formats for transactional merges.
- Orchestrator for retries, dependency, and cutover steps.

## Reliability Strategy
- Bulk load by immutable manifest files.
- Incremental CDC with offset checkpoints.
- Idempotent upsert in target tables.
- End-to-end checksums and reconciliation.
- Retry failed chunks and partial partition replays.

## Real-World Challenges
- **Skew:** huge partitions transfer slower—split into chunks.
- **Late/duplicate CDC:** sequence-based dedup and ordering windows.
- **Schema evolution:** mapping layer with compatibility checks.
- **Backfill:** replay historical windows into staging then merge.

## Performance and Scaling
- Parallel chunk transfer by partition.
- Compression in transit.
- Autoscaling workers for validation and merge.
- Partition pruning at target writes.

## Failure Recovery and Idempotency
- Resume from transfer manifests.
- Checkpoint CDC offsets per topic/table.
- Reconcile and replay failed tables only.
- Rollback via target table snapshots.

## Interview Questions
1. How do you prove zero-data-loss during migration?
2. Bulk + CDC design trade-offs?
3. How to perform cutover with near-zero downtime?
4. How do you handle incompatible schema types?
5. What metrics define migration readiness?
