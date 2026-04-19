# Azure Databricks

## 1) What is the Service?
Azure Databricks is a managed Apache Spark platform optimized for large-scale data engineering, analytics, and ML on Azure.  
It provides collaborative notebooks, job clusters, Delta Lake, and tight integration with ADLS, ADF, Synapse, and Unity Catalog.

---

## 2) When to Use?
Use Databricks when you need:
- Large-scale ETL/ELT (TB-PB)
- Streaming + batch unification
- Advanced Spark optimization and autoscaling
- Lakehouse patterns with ACID tables (Delta)
- Team collaboration and production scheduling

---

## 3) Architecture Usage
Common role:
- Read raw data from ADLS
- Clean/enrich into Delta bronze/silver/gold layers
- Serve curated datasets to Synapse/Power BI

### Batch pattern
`ADF trigger → Databricks jobs → Delta tables in ADLS → Synapse SQL serving`

### Streaming pattern
`Event Hubs → Structured Streaming in Databricks → Delta Live Tables / Gold marts`

---

## 4) Real-World Example
### Netflix-like Streaming Analytics
- Billions of watch events/day
- Databricks handles sessionization, anomaly detection, QoE metrics
- Gold tables power product dashboards and recommender features

### Uber-like Mobility Metrics
- Near real-time city demand forecasting
- Spark Structured Streaming computes rolling KPIs by geohash/time window

---

## 5) Integration with Other Services
- **ADF**: orchestration and dependency control
- **ADLS**: storage layers
- **Event Hubs**: real-time ingestion
- **Synapse**: warehouse serving and BI
- **Unity Catalog + Purview**: governance and lineage
- **Key Vault**: secret management

---

## 6) Common Mistakes
1. Using wide transformations without partition strategy
2. Too many tiny files causing metadata overhead
3. Not using Delta optimizations (OPTIMIZE/Z-ORDER/VACUUM)
4. Over-provisioned always-on clusters for sporadic workloads
5. Ignoring skew in joins and aggregations

---

## 7) Performance Tips
- Use Delta format by default
- Use Auto Loader for scalable file ingestion
- Compact small files regularly
- Tune shuffle partitions and AQE settings
- Use cluster policies and job clusters for cost control
- Cache only hot intermediate data
- Prefer MERGE with appropriate predicates and partition pruning

### Cost Tips
- Use spot VMs where SLA allows
- Prefer ephemeral job clusters over interactive clusters for production jobs
- Set auto-termination aggressively

---

## 8) 🔥 Interview Questions

### Conceptual
1. Why Delta Lake over plain Parquet in production?
2. What is the bronze-silver-gold model?
3. How does Unity Catalog improve governance?

### Scenario-Based
4. Pipeline latency doubled after data growth. What do you check first?
5. How do you process late-arriving streaming data correctly?
6. How do you design idempotent incremental merges?

### Product/Comparison
7. **Databricks vs Synapse**
   - Databricks: Spark-first lakehouse, advanced ETL/ML workloads
   - Synapse: SQL DW + integrated analytics workspace
8. **Databricks vs EMR vs Dataproc**
   - Databricks: richest lakehouse + productivity
   - EMR/Dataproc: lower-level cluster control; can be cheaper with strong ops teams

### Follow-ups
9. Explain Z-ORDER and when it helps.
10. How do you handle schema evolution safely in Delta pipelines?
