# Google Cloud Storage (GCS)

## 1) What is the Service?
GCS is GCP’s object storage service, commonly used as the foundational data lake storage layer.

## 2) When to Use?
- Raw/processed/curated lake zones
- Batch and stream output landing
- Low-cost archival of historical data

## 3) Architecture Usage
`Ingestion/Processing services → GCS zones → BigQuery external/load workflows`

## 4) Real-World Example
Content analytics platform:
- Logs and event exports stored in partitioned GCS paths
- BigQuery reads curated partitions for business reporting

## 5) Integration with Other Services
- Dataflow and Dataproc
- BigQuery external tables/load jobs
- Pub/Sub notifications on object changes

## 6) Common Mistakes
- No lifecycle policies
- Poor folder/partition naming standards
- Too many tiny files from streaming sinks

## 7) Performance Tips
- Prefer columnar formats and compression
- Partition folder structure by date/domain
- Use lifecycle transitions for cold data
- Compact small files periodically

## 8) 🔥 Interview Questions
1. S3 vs ADLS vs GCS?
2. How to design GCS path conventions for multi-tenant pipelines?
3. How to optimize BigQuery reads from GCS-backed data?
