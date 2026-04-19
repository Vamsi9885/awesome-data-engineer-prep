# Azure Synapse Analytics

## 1) What is the Service?
Azure Synapse is an integrated analytics platform combining SQL data warehousing, Spark, and data integration capabilities in one workspace.  
For data engineers, Synapse is often the **serving and analytical SQL layer** on top of lake/warehouse data.

---

## 2) When to Use?
Use Synapse when you need:
- Enterprise SQL analytics and BI serving
- MPP warehouse workloads
- Tight integration with ADLS and Power BI
- Mixed SQL + Spark analytics in one Azure-native environment

---

## 3) Architecture Usage
Synapse commonly sits at the consumption layer:
- Curated data from ADLS/Databricks loaded into dedicated SQL pool
- Serverless SQL used for ad-hoc query on lake files
- Dashboards connect via Power BI

### Pattern
`ADF orchestration → ADLS + Databricks transforms → Synapse SQL marts → BI`

---

## 4) Real-World Example
### Retail (Amazon-style) Margin Analytics
- Gold-level sales, returns, promotion datasets loaded to Synapse
- Dedicated SQL pool serves executive dashboards
- Serverless SQL used by analysts for exploratory one-off checks

### Streaming + Batch Hybrid
- Event Hubs stream summarized into near-real-time tables
- Nightly batch reconciles and overwrites final reporting partitions

---

## 5) Integration with Other Services
- **ADF** for orchestration and data movement
- **ADLS** as lake storage
- **Databricks** for heavy transformations
- **Power BI** for visualization
- **Purview** for governance and lineage
- **Key Vault / Managed Identity** for secure credential handling

---

## 6) Common Mistakes
1. Using dedicated pool for sporadic ad-hoc workloads (costly)
2. Not choosing proper distribution key / partitioning in warehouse tables
3. Overloading one giant fact table without workload management
4. Ignoring result set caching/materialized views
5. Using serverless SQL for highly repetitive heavy workloads

---

## 7) Performance Tips
- Use columnstore indexes for large fact tables
- Choose HASH distribution for large joins on common key
- Partition large tables by date/time where query predicates align
- Use materialized views for repeated aggregates
- Scale compute based on ETL/BI windows
- Use workload groups to isolate critical dashboards

### Cost Tips
- Pause/resume dedicated pools outside business windows
- Use serverless SQL for true ad-hoc exploration
- Keep external file formats optimized (Parquet/Delta)

---

## 8) 🔥 Interview Questions

### Conceptual
1. Serverless SQL pool vs Dedicated SQL pool?
2. Why does distribution strategy matter in MPP systems?
3. Synapse vs traditional SQL warehouse architecture?

### Scenario-Based
4. Dashboard latency spikes at month-end close. What do you tune first?
5. How do you design fact/dimension loading with late arriving dimensions?
6. How do you support both ad-hoc analysts and mission-critical dashboards safely?

### Product/Comparison
7. **Databricks vs Synapse**
   - Databricks stronger for Spark-first ETL/ML/lakehouse
   - Synapse stronger for integrated SQL warehouse serving
8. **Synapse vs Redshift vs BigQuery**
   - Synapse: Azure enterprise + Power BI integration
   - Redshift: AWS-native MPP control
   - BigQuery: serverless simplicity

### Follow-up
9. How to choose distribution key for a 10TB orders fact?
10. How to migrate from on-prem DW to Synapse with minimal downtime?
