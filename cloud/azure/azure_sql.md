# Azure SQL Database

## 1) What is the Service?
Azure SQL Database is a managed relational database service for transactional and analytical-support workloads.

## 2) When to Use?
- OLTP systems feeding analytics
- Small-to-medium dimensional marts
- Metadata/config stores with SQL requirements

## 3) Architecture Usage
`Apps/OLTP → Azure SQL → ADF/Databricks extraction → ADLS/Synapse`

## 4) Real-World Example
Subscription platform:
- Billing and account transactions in Azure SQL
- Incremental CDC extracts to lake for finance analytics and churn models

## 5) Integration with Other Services
- ADF for extraction/orchestration
- Databricks for transformations
- Synapse for serving
- Key Vault + private endpoints for secure access

## 6) Common Mistakes
- Running heavy analytics directly on OLTP primary
- Missing indexing for extraction predicates
- No read replica strategy for ETL load isolation

## 7) Performance Tips
- Use partitioning/indexing aligned to extraction windows
- Use incremental loads over full table scans
- Leverage read scale-out for reporting/extraction
- Keep transactions short and stable

## 8) 🔥 Interview Questions
1. Azure SQL vs Cosmos DB for metadata stores?
2. How do you build CDC from Azure SQL to ADLS?
3. OLTP source performance degrades during ETL—how do you fix?
