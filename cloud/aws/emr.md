# AWS EMR (Elastic MapReduce)

## 1) What is the Service?
EMR is AWS’s managed big-data cluster service for Spark/Hadoop/Flink/Presto workloads.

## 2) When to Use?
- Large custom Spark ETL/ML
- Fine-grained cluster-level tuning
- Workloads needing custom libraries/runtime control

## 3) Architecture Usage
`S3 raw → EMR Spark jobs → S3 curated → Athena/Redshift`

## 4) Real-World Example
Netflix-like session analytics:
- Daily + hourly Spark jobs on trillions of events
- Heavy joins, feature generation, and quality scoring

## 5) Integration with Other Services
- S3, Glue Catalog, Athena, Redshift Spectrum
- Step Functions for orchestration
- CloudWatch for monitoring

## 6) Common Mistakes
- Overprovisioned static clusters
- No spot strategy
- Ignoring shuffle and skew tuning
- Running tiny jobs on huge clusters

## 7) Performance Tips
- Use spot + on-demand mix
- Tune executor memory/cores and shuffle partitions
- Enable autoscaling and right-size node families
- Store outputs in optimized Parquet partition layouts

## 8) 🔥 Interview Questions
1. Glue vs EMR: when choose each?
2. How would you reduce EMR cost by 40%?
3. EMR vs Databricks vs Dataproc tradeoffs?
