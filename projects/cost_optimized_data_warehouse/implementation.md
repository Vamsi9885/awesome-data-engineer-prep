# Cost Optimized Data Warehouse — Implementation

## Implementation Flow
1. Land raw data incrementally into bronze partitions.
2. Build conformed silver models using dbt incremental + merge.
3. Build gold marts using selective denormalization and pre-aggregates.
4. Apply workload isolation (ETL warehouse vs BI warehouse).
5. Enable query result cache and semantic model cache.
6. Collect cost telemetry per query/user/team.
7. Run nightly optimization (compaction, clustering, stale table cleanup).

## Reliability Strategy
- Incremental watermark state table.
- Idempotent merge on business keys.
- Retry orchestration with max attempts and alerting.
- Data quality assertions pre-publish.
- Time-travel rollback for failed release.

## Real-World Challenges
- **Skew:** avoid single huge partitions; rebalance clustering keys.
- **Late data:** restatement windows for trailing days.
- **Duplicates:** dedup in staging layer before gold.
- **Schema evolution:** contract-based model tests in CI.
- **Backfill:** bounded historical backfill with isolated compute.

## Performance & Scaling
- Partition facts by date, cluster by frequent filter columns.
- Use incremental snapshots for slowly changing dimensions.
- Materialize expensive joins as precomputed tables.
- Compression and column pruning for scan reduction.
- Warehouse auto-suspend + concurrency scaling for burst traffic.

## Recovery and Idempotency
- Re-run by date partition safely.
- Persist job run metadata and row counts.
- Automatic rollback to previous snapshot on anomaly.
- Alert on cost anomalies and query outliers.

## Interview Questions
1. How do you choose partition and clustering keys?
2. What causes unnecessary scan cost and how to detect it?
3. How to optimize incremental model correctness?
4. When to denormalize marts vs keep star schema?
5. How would you implement cost chargeback by team?
