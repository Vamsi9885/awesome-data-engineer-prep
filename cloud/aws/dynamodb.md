# Amazon DynamoDB

## 1) What is the Service?
DynamoDB is AWS’s fully managed NoSQL key-value/document database designed for low-latency at massive scale.

## 2) When to Use?
- High-throughput operational metadata
- Idempotency keys and state tracking
- Real-time feature/lookup tables in pipelines

## 3) Architecture Usage
`Streaming/Batches → Lambda/ETL → DynamoDB (state/lookup) → downstream joins`

## 4) Real-World Example
Ride-hailing state store:
- Current trip status keyed by trip_id
- Fast lookups for dispatch and monitoring systems

## 5) Integration with Other Services
- Lambda triggers via Streams
- API Gateway
- Kinesis integration patterns
- S3 export for analytics

## 6) Common Mistakes
- Poor partition key leading to hot partitions
- Overusing scans
- Ignoring access pattern design upfront

## 7) Performance Tips
- Model by access patterns first
- Use composite keys and sparse GSIs smartly
- Use on-demand vs provisioned capacity appropriately
- Enable TTL for ephemeral records

## 8) 🔥 Interview Questions
1. How to design DynamoDB keys for event deduplication?
2. DynamoDB vs RDS for operational metadata?
3. How do GSIs affect cost and consistency?
