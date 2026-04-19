# Azure Data Lake Storage (ADLS Gen2)

## 1) What is the Service?
ADLS Gen2 is Azure’s scalable, secure object storage optimized for analytics workloads.  
It combines Blob Storage economics with a hierarchical namespace for filesystem-like operations.

---

## 2) When to Use?
Use ADLS when you need:
- Central data lake for raw-to-curated zones
- Cheap, durable storage for structured/semi/unstructured data
- Fine-grained ACL/RBAC for enterprise governance
- Multi-engine access (Databricks, Synapse, Spark, SQL engines)

---

## 3) Architecture Usage
Standard medallion/storage zone model:
- **Raw/Bronze**: immutable landing from sources
- **Processed/Silver**: cleaned and standardized
- **Curated/Gold**: business-ready analytical datasets

### Azure Batch Architecture
`ADF → ADLS(raw) → Databricks(silver/gold) → Synapse(serving)`

ADLS is the persistent layer across all stages.

---

## 4) Real-World Example
### Amazon-like Marketplace Lake
- Clickstream, orders, catalog, logistics feeds land in ADLS
- Databricks creates Delta tables partitioned by date/region
- Synapse serves finance and operations dashboards

### Netflix-like Content Telemetry
- Watch/device/error logs stored in time-partitioned folders
- Tiering applied: hot (recent), cool/archive (historical)

---

## 5) Integration with Other Services
- **ADF** for ingestion/orchestration
- **Databricks** for large-scale transformation
- **Synapse** for SQL serving and ELT
- **Event Hubs + ASA** for streaming landing
- **Purview** for catalog and lineage
- **Key Vault + Private Endpoints** for secure access

---

## 6) Common Mistakes
1. No clear folder conventions (`source/system/table/dt=...`)
2. Too many small files (poor query performance)
3. Skipping lifecycle management (high storage cost)
4. No partition strategy aligned to query predicates
5. Weak permission model (overbroad access)

---

## 7) Performance Tips
- Use columnar formats (Parquet/Delta) over JSON/CSV for analytics
- Partition by high-selectivity, common filters (e.g., dt, region)
- Compact small files regularly
- Separate storage account for heavy concurrent workloads when needed
- Use lifecycle policies (hot/cool/archive tiers)
- Keep schema and naming conventions strict across producers

### Cost Tips
- Archive cold data with policy automation
- Avoid frequent full rewrites; use incremental append/merge
- Compress files and optimize row group sizes

---

## 8) 🔥 Interview Questions

### Conceptual
1. ADLS Gen2 vs Blob Storage: what changes with hierarchical namespace?
2. Why is ADLS better than RDBMS for raw event retention?
3. What is the purpose of bronze/silver/gold in lake design?

### Scenario-Based
4. Your Synapse queries on ADLS are slow—what do you optimize first?
5. How do you design folder and partition standards for 200 datasets?
6. How do you enforce PII access controls for only specific teams?

### Product/Comparison
7. **S3 vs ADLS vs GCS**
   - Similar object-store foundations
   - ADLS stands out in Azure-native ACL semantics and enterprise integration
8. **ADLS + Databricks vs Synapse-only**
   - Databricks for heavy Spark ETL
   - Synapse-only may suit SQL-heavy teams with less Spark complexity

### Follow-up
9. How to manage schema evolution across yearly historical partitions?
10. How to handle backfills safely without breaking downstream consumers?
