# Google Pub/Sub

## 1) What is the Service?
Pub/Sub is GCP’s global messaging and event ingestion service for asynchronous, scalable data pipelines.

## 2) When to Use?
- Event-driven architectures
- Real-time pipeline ingress
- Decoupling producers and consumers

## 3) Architecture Usage
`Apps/Services → Pub/Sub topics → Dataflow/Functions/Dataproc → BigQuery/GCS`

## 4) Real-World Example
Real-time order platform:
- Checkout events published to Pub/Sub
- Dataflow computes KPIs and anomaly metrics
- BigQuery dashboards update in near real time

## 5) Integration with Other Services
- Dataflow streaming pipelines
- Cloud Functions triggers
- BigQuery subscriptions (patterns)
- GCS archival workflows

## 6) Common Mistakes
- No dead-letter topics
- Ignoring message ordering/duplicate handling constraints
- Weak retry and ack deadline tuning

## 7) Performance Tips
- Tune ack deadlines and flow control
- Use batching for publishers
- Partition topics by domain/criticality
- Monitor backlog and consumer lag

## 8) 🔥 Interview Questions
1. Pub/Sub vs Kinesis vs Event Hubs?
2. How to design idempotent consumers in at-least-once delivery?
3. How to handle poisoned messages safely?
