# Cost Optimized Data Warehouse — Architecture

## Architecture Diagram (Text)
```text
[Operational DBs / SaaS / Events]
             |
             v
      [Ingestion Layer]
 (Batch ELT + CDC Incrementals)
             |
             v
      [Raw/Bronze Storage]
             |
             v
   [Transform Engine + dbt]
  (incremental models, snapshots)
             |
      +------+------+
      |             |
      v             v
 [Silver Core]   [Cost Metrics Mart]
      |             |
      +------+------+
             v
        [Gold Marts]
(Finance/Marketing/Ops dashboards)
             |
             v
   [BI + Semantic Layer + Caching]
```

## Service Choices and Justification
- **Object storage + warehouse tables:** low storage cost and scalable separation of compute/storage.
- **Incremental ELT (dbt/Spark SQL):** avoid full refresh, minimize scan bytes.
- **Query engine autoscaling:** isolates spiky workloads.
- **Result cache/materialized views:** reduce repeated expensive queries.
- **Cost observability tables:** per-query and per-team spend attribution.

## Reliability Strategy
- Idempotent incremental loads keyed by watermark + primary key.
- Retry policies for transient failures.
- Checkpoint table for last successful load.
- Data quality gates before publishing to gold.
- Rollback strategy using table snapshots/time travel.

## Real-World Challenges
- **Skew:** high-cardinality customer/product data can hotspot.
- **Late arrivals:** delayed order events alter daily metrics.
- **Duplicates:** retries in upstream ingestion.
- **Schema evolution:** new business attributes.
- **Backfills:** historical restatements from finance policy changes.

## Performance and Cost Strategy
- Partition fact tables by event_date.
- Cluster/sort by high-selectivity dimensions (customer_id, product_id).
- Compact small files and optimize metadata.
- Use columnar format (Parquet/Delta) with compression.
- Separate virtual warehouses for ETL vs BI.
- Auto-suspend idle compute and concurrency scaling.
- Precompute heavy aggregates for common dashboards.

## Failure Recovery and Idempotency
- Rerun-safe merges with deterministic keys.
- Snapshot rollback for bad transformations.
- Dead-letter records for quality violations.
- SLA alerts for stale models and cost spikes.

## Interview Questions
1. How do you reduce warehouse costs without hurting SLA?
2. Partitioning vs clustering trade-offs?
3. When to use materialized view vs cached result?
4. How do incremental models fail and recover?
5. How do you do chargeback for analytics teams?
