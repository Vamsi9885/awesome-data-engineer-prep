# Amazon Athena

## 1) What is the Service?
Athena is a serverless query engine to run SQL directly on data in S3 using the Glue Data Catalog.

## 2) When to Use?
- Ad hoc analysis on S3 data lake
- Lightweight BI and exploration
- Fast time-to-insight without cluster provisioning

## 3) Architecture Usage
`S3 curated + Glue Catalog → Athena SQL → dashboards/reports`

## 4) Real-World Example
Amazon-style operations analytics:
- Analysts query order delay patterns on partitioned Parquet tables in S3
- No warehouse provisioning needed for exploratory workloads

## 5) Integration with Other Services
- S3, Glue Catalog, Lake Formation
- QuickSight
- Step Functions for CTAS optimization workflows

## 6) Common Mistakes
- Querying non-columnar raw JSON directly
- No partition projection
- SELECT * on wide tables
- Unbounded scans with missing date filters

## 7) Performance Tips
- Use Parquet/ORC + compression
- Partition by dt/region and enforce filter predicates
- Use CTAS to optimize historical datasets
- Use workgroups, query limits, and budgets

## 8) 🔥 Interview Questions
1. Athena vs Redshift?
2. Why does Athena bill by scanned data and how to reduce it?
3. How would you optimize a 30-minute Athena query?
