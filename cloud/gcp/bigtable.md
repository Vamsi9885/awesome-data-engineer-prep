# Google Cloud Bigtable

## 1) What is the Service?
Bigtable is GCP’s wide-column NoSQL database optimized for large-scale, low-latency key-based access.

## 2) When to Use?
- Time-series telemetry at very high write rates
- Real-time feature stores
- Sparse, large keyspace operational data

## 3) Architecture Usage
`Streams/Dataflow → Bigtable (serving state) → periodic export to BigQuery/GCS`

## 4) Real-World Example
Video analytics counters:
- Per-title/per-region time-series metrics updated in near real time
- Dashboard APIs read hot metrics with low latency

## 5) Integration with Other Services
- Dataflow sinks/sources
- AI/feature pipelines
- BigQuery export patterns for historical analytics

## 6) Common Mistakes
- Poor row-key design causing hotspots
- Expecting relational query capabilities
- Storing too many versions without retention controls

## 7) Performance Tips
- Design row keys for write/read distribution
- Keep rows reasonably sized
- Use app profiles and replication appropriately
- Plan TTL/versioning policy early

## 8) 🔥 Interview Questions
1. Bigtable vs BigQuery use cases?
2. How do row-key choices affect performance?
3. Bigtable vs DynamoDB/Cosmos DB for event-state workloads?
