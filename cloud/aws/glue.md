# AWS Glue

## 1) What is the Service?
AWS Glue is a serverless data integration service for ETL, metadata cataloging, and job orchestration in AWS analytics stacks.

## 2) When to Use?
- Managed ETL without cluster ops
- Metadata catalog for Athena/EMR/Redshift Spectrum
- Incremental batch processing with bookmarks

## 3) Architecture Usage
`S3 raw → Glue Crawler/Catalog → Glue ETL → S3 curated → Athena/Redshift`

## 4) Real-World Example
E-commerce pipeline:
- Crawl new partner datasets daily
- Standardize schema with Glue ETL
- Publish curated Parquet for downstream BI

## 5) Integration with Other Services
- S3, Athena, EMR, Redshift Spectrum
- Lake Formation
- Step Functions/EventBridge orchestration

## 6) Common Mistakes
- Overusing crawlers on stable schemas
- DynamicFrames for all workloads (can be slower than DataFrames)
- No partition pruning in ETL outputs

## 7) Performance Tips
- Use Spark DataFrame API where performance matters
- Partition output aggressively by query predicates
- Enable job bookmarks for incremental loads
- Pushdown predicates to reduce scanned data

## 8) 🔥 Interview Questions
1. Glue vs EMR for ETL?
2. How do Glue bookmarks work and where do they fail?
3. How to design Glue Catalog for 10k tables?
