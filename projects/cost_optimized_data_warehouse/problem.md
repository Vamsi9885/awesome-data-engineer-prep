# Cost Optimized Data Warehouse — Problem Statement

## Business Context
A fast-growing e-commerce company’s warehouse costs are rising faster than revenue due to inefficient storage, unbounded query scans, and redundant transformations. Finance requires predictable spend while analytics teams need performance SLAs.

## Functional Requirements
- Build a warehouse architecture optimized for cost and performance.
- Separate hot interactive workloads from heavy batch transformations.
- Implement storage lifecycle and data tiering.
- Introduce incremental models and materialization strategy.
- Track per-team and per-query cost attribution.
- Provide curated marts for finance, marketing, and operations.

## Non-Functional Requirements
- 35% reduction in monthly warehouse spend.
- P95 dashboard query latency < 8 seconds.
- 99.9% pipeline success.
- Idempotent batch reruns and deterministic outputs.
- Governance, access control, and audit logging.

## Data Challenges
- Over-partitioned and under-clustered tables.
- Small-file proliferation.
- Duplicate ETL jobs producing redundant tables.
- Inconsistent model ownership and SLAs.
- Backfills causing massive full-table scans.

## Success Metrics
- Cost per query reduced by 40%.
- Storage growth rate reduced by 30%.
- SLA breaches < 1% monthly.
