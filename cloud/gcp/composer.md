# Google Cloud Composer

## 1) What is the Service?
Cloud Composer is GCP’s managed Apache Airflow service for workflow orchestration.

## 2) When to Use?
- Code-first DAG orchestration
- Multi-system dependency handling
- Scheduled/triggered ETL workflows at scale

## 3) Architecture Usage
`Composer DAGs → Dataflow/Dataproc/BigQuery jobs → monitoring + alerts`

## 4) Real-World Example
Marketplace orchestration:
- DAG validates source drops
- Runs Dataproc batch + BigQuery quality checks
- Publishes success/failure notifications

## 5) Integration with Other Services
- BigQuery operators
- Dataflow templates
- Dataproc operators
- Pub/Sub triggers and Cloud Storage sensors

## 6) Common Mistakes
- Monolithic DAGs with poor modularity
- Heavy compute inside Airflow workers
- No clear retry/timeout policies

## 7) Performance Tips
- Keep tasks idempotent
- Use task groups and reusable DAG factories
- Externalize configs and environment variables
- Tune scheduler/executor settings for DAG volume

## 8) 🔥 Interview Questions
1. Composer vs ADF vs Step Functions?
2. How to design robust DAG retries and SLA alerts?
3. Why Airflow should orchestrate, not process data?
