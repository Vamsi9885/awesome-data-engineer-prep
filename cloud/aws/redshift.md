# Amazon Redshift

## 1) What is the Service?
Redshift is AWS’s managed MPP data warehouse for high-performance analytical SQL workloads.

## 2) When to Use?
- Complex BI/reporting with high concurrency
- Star-schema marts and historical analytical datasets
- Predictable heavy SQL workloads

## 3) Architecture Usage
`S3 curated → COPY/ELT into Redshift → BI tools`

## 4) Real-World Example
E-commerce finance reporting:
- Revenue, margin, returns marts refreshed hourly
- Leadership dashboards require strict SLA and concurrency

## 5) Integration with Other Services
- S3 + Spectrum
- Glue Catalog
- Kinesis/Lambda (near-real-time loads)
- QuickSight/Tableau/Power BI

## 6) Common Mistakes
- Poor distribution/sort key design
- Not vacuuming/analyzing when needed
- Loading too many tiny batches
- Using Redshift for transient ad hoc-only workloads

## 7) Performance Tips
- Choose dist key by largest join path
- Use sort keys aligned to filter patterns
- Use column encoding/compression
- Use RA3 + managed storage and concurrency scaling

## 8) 🔥 Interview Questions
1. Athena vs Redshift: when and why?
2. How to pick sort/dist keys for orders fact?
3. Redshift vs BigQuery vs Snowflake for enterprise BI?
