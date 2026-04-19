# Problem Statement — Multi-Cloud Data Lake Pipeline

## Business Context

A global e-commerce marketplace operates regionally due to compliance and latency constraints:
- North America workloads on AWS
- Europe workloads on Azure
- APAC workloads on GCP

Each region stores raw operational data independently (orders, catalog, payments, clickstream). Executives and data scientists need a **single trusted analytics layer** for demand forecasting, customer 360, and margin analysis.

Current failures:
- inconsistent schema definitions across clouds
- duplicate records during retries and cross-region replays
- no standard late-data correction policy
- cost spikes caused by small-file explosion and unbounded compute

---

## Functional Requirements

1. Ingest daily + hourly feeds from:
   - AWS S3 (JSON/Parquet)
   - Azure ADLS Gen2 (CSV/Parquet)
   - GCP Cloud Storage (Avro/Parquet)
2. Normalize to a canonical schema contract.
3. Build bronze/silver/gold zones with lineage and reproducibility.
4. Publish curated data to:
   - Snowflake (global BI users)
   - BigQuery (APAC advanced analytics)
5. Handle schema evolution without full pipeline rewrites.
6. Support backfill of historical partitions (minimum 36 months).
7. Enforce deduplication across cloud sources using deterministic keys.

---

## Non-Functional Requirements

- Data freshness:
  - hourly silver refresh (< 25 min lag)
  - daily gold SLA by 05:30 UTC
- Availability: 99.95% successful production runs
- RPO: <= 15 minutes for streaming-derived datasets
- RTO: <= 60 minutes for failed partition replay
- Security:
  - cloud-native IAM + service principals
  - encryption in transit and at rest
  - PII tokenization in silver
- Governance:
  - dataset ownership, quality SLAs, and lineage metadata
- Cost:
  - keep storage+compute within monthly FinOps budget with alerting

---

## Data Volumes & Constraints

- Orders: 150M/day
- Clickstream events: 4.2B/day
- Product catalog updates: 25M/day
- Average daily raw ingest: 14–18 TB compressed
- Peak season multiplier: 3.5x
- Regional schema drift from independent product teams
- Country-level data residency rules restrict raw movement

---

## Real-World Challenges to Solve

- Data skew: top countries dominate order volume
- Late-arriving data: payment updates can lag by 48 hours
- Duplicate handling: retries from regional ingestion jobs
- Schema evolution: additive/breaking changes from partner APIs
- Backfills: replay historical data without corrupting current snapshots

---

## Success Criteria

1. Global KPI variance between Snowflake and BigQuery < 0.1%.
2. Duplicate leakage into gold < 0.01%.
3. Backfill of one year completes in < 8 hours with no manual fixes.
4. 95th percentile daily SLA met for 3 consecutive months.
5. Interview readiness:
   - explain why canonical schema + contract testing is mandatory
   - explain trade-offs of centralization vs federated compute
   - explain exactly-once semantics and idempotent backfills

---

## Interview Questions (Project-Specific)

### Conceptual
1. Why did you choose a lakehouse medallion model over direct warehouse ELT?
2. Why maintain both Snowflake and BigQuery serving layers?

### Trade-offs
3. Spark on Databricks vs Dataflow for cross-cloud processing—why?
4. Delta Lake vs plain Parquet for silver/gold reliability—why?

### Scaling
5. What breaks first at 10x clickstream volume and how do you prevent it?
6. How do you avoid driver and shuffle bottlenecks under skewed keys?

### Failure Scenarios
7. What happens if one cloud’s ingestion fails but others succeed?
8. How do you recover from partial MERGE completion in silver?

### Optimization
9. How do you reduce cross-cloud egress cost while preserving consistency?
10. How do compaction and Z-ordering affect both performance and cost?
