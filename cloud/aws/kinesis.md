# Amazon Kinesis

## 1) What is the Service?
Kinesis is AWS’s managed streaming data platform for ingesting and processing real-time data at scale.

## 2) When to Use?
- Clickstream, telemetry, order events
- Near-real-time analytics pipelines
- Stream buffering before ETL/warehouse loads

## 3) Architecture Usage
`Producers → Kinesis Data Streams → Lambda/EMR/Flink → S3/Redshift`

## 4) Real-World Example
Black Friday stream:
- Orders/events ingested to Kinesis
- Lambda enriches and stores raw + clean events in S3
- Athena dashboards refresh every few minutes

## 5) Integration with Other Services
- Lambda, Kinesis Data Analytics (Flink)
- Firehose to S3/Redshift/OpenSearch
- EMR Spark streaming

## 6) Common Mistakes
- Poor shard sizing
- No consumer lag monitoring
- No partition key strategy
- Relying on strict global ordering

## 7) Performance Tips
- Design partition keys for even shard distribution
- Use enhanced fan-out for multiple low-latency consumers
- Batch producer writes
- Auto-scale shard counts as traffic changes

## 8) 🔥 Interview Questions
1. Kinesis vs Kafka?
2. Kinesis vs Event Hubs vs Pub/Sub?
3. How do you choose shard count and partition key?
