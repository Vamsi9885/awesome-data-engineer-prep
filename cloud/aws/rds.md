# Amazon RDS for Data Engineers

## 1) What is the Service?
Amazon RDS is a managed relational database service (MySQL, PostgreSQL, SQL Server, etc.) for OLTP and operational workloads.

## 2) When to Use?
- Source systems feeding analytical pipelines
- Transactional systems requiring ACID
- Metadata/config repositories needing SQL semantics

## 3) Architecture Usage
`Application OLTP on RDS → CDC/Batch extract → S3/Lake/Warehouse`

## 4) Real-World Example
E-commerce order system:
- Orders stored in Aurora PostgreSQL
- CDC streams changes to analytics lake for near-real-time reporting

## 5) Integration with Other Services
- DMS for migration/CDC
- Glue/EMR extract jobs
- Lambda for event-driven workflows
- Redshift for analytics serving

## 6) Common Mistakes
- Running analytics directly on primary OLTP instance
- Missing index strategy on extraction queries
- No replica usage for ETL read isolation

## 7) Performance Tips
- Use read replicas for extraction/reporting load
- Incremental extraction with watermarks/CDC
- Proper indexing and query plans
- Tune connection pools and transaction sizes

## 8) 🔥 Interview Questions
1. RDS vs DynamoDB in data pipelines?
2. How to replicate OLTP data to lake with minimal source impact?
3. Why CDC is preferred over full extracts for large tables?
