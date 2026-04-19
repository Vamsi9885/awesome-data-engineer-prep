# Google BigQuery

## 1) What is the Service?
BigQuery is GCP’s serverless, columnar data warehouse for petabyte-scale analytics using SQL.

## 2) When to Use?
- Fast analytical queries without cluster management
- Enterprise BI and ad hoc analytics
- SQL-first teams requiring high concurrency

## 3) Architecture Usage
`Pub/Sub/Dataflow/Dataproc → BigQuery curated marts → BI/ML`

## 4) Real-World Example
Uber-like mobility analytics:
- Trips streamed and batch-loaded into partitioned tables
- City-level surge, ETA, and demand dashboards on BigQuery

## 5) Integration with Other Services
- Dataflow streaming/batch
- Pub/Sub ingest patterns
- GCS external tables
- Looker and BI tools
- BigQuery ML

## 6) Common Mistakes
- No partition/clustering strategy
- Repeated scanning of wide raw tables
- Ignoring slots/workload management for heavy concurrency

## 7) Performance Tips
- Partition by ingestion or business date
- Cluster on high-cardinality filter dimensions
- Use materialized views for repeated aggregations
- Prune selected columns and avoid SELECT *

## 8) 🔥 Interview Questions
1. BigQuery vs Redshift vs Snowflake?
2. How to optimize cost when scans exceed budget?
3. Partitioning vs clustering in BigQuery?
