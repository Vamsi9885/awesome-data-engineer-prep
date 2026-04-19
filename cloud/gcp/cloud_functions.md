# Google Cloud Functions

## 1) What is the Service?
Cloud Functions is GCP’s serverless event-driven compute service for lightweight logic execution.

## 2) When to Use?
- Event enrichment/validation
- Trigger-based automations
- Lightweight API/webhook handlers

## 3) Architecture Usage
`Pub/Sub/GCS/Eventarc trigger → Cloud Functions → BigQuery/GCS/notifications`

## 4) Real-World Example
Real-time data hygiene:
- Functions validate incoming event schema
- Invalid events routed to quarantine
- Valid events forwarded for Dataflow processing

## 5) Integration with Other Services
- Pub/Sub triggers
- Cloud Storage triggers
- Firestore triggers
- BigQuery write patterns

## 6) Common Mistakes
- Heavy transformations in functions
- No idempotency in retried executions
- Ignoring cold-start tradeoffs

## 7) Performance Tips
- Keep execution units short and focused
- Reuse clients and avoid repeated initialization
- Use Cloud Run where workload outgrows function limits

## 8) 🔥 Interview Questions
1. Cloud Functions vs Lambda vs Azure Functions?
2. How to design retry-safe event processing?
3. When to move from Functions to Dataflow/Dataproc?
