# Azure Cosmos DB

## 1) What is the Service?
Cosmos DB is Azure’s globally distributed, low-latency NoSQL database with multiple APIs and tunable consistency.

## 2) When to Use?
- High-scale operational metadata
- User/session/profile stores
- Global applications with multi-region replication

## 3) Architecture Usage
`Apps/Streams → Cosmos DB (operational state) → ETL export to ADLS/Synapse for analytics`

## 4) Real-World Example
Streaming personalization:
- Session state and recommendations context stored in Cosmos DB
- Batch pipelines periodically export operational snapshots for model retraining

## 5) Integration with Other Services
- Azure Functions (change feed processing)
- Event Hubs
- ADF/Synapse Link patterns
- Databricks connectors

## 6) Common Mistakes
- Bad partition key causing hot partitions
- Using strong consistency globally without latency/cost tradeoff awareness
- OLAP-style joins attempted directly in Cosmos DB

## 7) Performance Tips
- Design partition key by dominant access patterns
- Use change feed for incremental downstream processing
- Choose consistency model carefully (session/eventual often enough)
- Manage RU/s autoscale for bursty traffic

## 8) 🔥 Interview Questions
1. Cosmos DB vs DynamoDB?
2. How do you choose partition keys for event state?
3. When should Cosmos DB data be exported to lake/warehouse?
