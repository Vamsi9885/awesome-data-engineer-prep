# AWS Lambda

## 1) What is the Service?
Lambda is AWS serverless compute to run event-driven code without managing servers.

## 2) When to Use?
- Stream/event enrichment
- API/webhook handlers
- Lightweight ETL steps
- Glue/EMR workflow utility actions

## 3) Architecture Usage
`Kinesis/S3/EventBridge trigger → Lambda → S3/DynamoDB/Redshift`

## 4) Real-World Example
Uber-like event processor:
- Validate trip events
- Add metadata from config store
- Route anomalies to alerts and DLQ

## 5) Integration with Other Services
- Kinesis, S3, EventBridge
- DynamoDB, SQS, SNS
- Step Functions orchestration

## 6) Common Mistakes
- Long-running heavy transforms in Lambda
- Ignoring cold start impact
- No idempotency keys for retries

## 7) Performance Tips
- Keep packages small
- Reuse DB/network clients
- Tune memory (CPU scales with memory)
- Use reserved concurrency for critical functions

## 8) 🔥 Interview Questions
1. Lambda vs Fargate vs Glue Python shell?
2. How to handle duplicate events safely?
3. How to design low-latency Lambda in high-traffic streams?
