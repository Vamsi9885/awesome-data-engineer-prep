# Google Cloud Dataproc

## 1) What is the Service?
Dataproc is GCP’s managed Spark/Hadoop service for running big-data jobs with cluster-level control.

## 2) When to Use?
- Spark workloads needing custom tuning/runtime
- Lift-and-shift Spark/Hadoop jobs to GCP
- Batch ETL and ML feature pipelines

## 3) Architecture Usage
`GCS raw → Dataproc Spark jobs → GCS curated → BigQuery`

## 4) Real-World Example
Streaming service analytics:
- Nightly Spark jobs build recommendation features
- Cost-optimized with ephemeral clusters and autoscaling

## 5) Integration with Other Services
- GCS storage
- BigQuery load/output
- Composer orchestration
- Pub/Sub + Spark streaming patterns

## 6) Common Mistakes
- Long-lived idle clusters
- No preemptible worker strategy
- Ignoring shuffle/skew optimization

## 7) Performance Tips
- Use ephemeral clusters per pipeline
- Preemptible workers for cost reduction
- Tune Spark configs per workload profile
- Store outputs in partitioned Parquet/Delta-compatible formats

## 8) 🔥 Interview Questions
1. Dataproc vs Databricks vs EMR?
2. When not to use Dataproc and choose Dataflow instead?
3. How to design low-cost, high-throughput Spark jobs on GCP?
