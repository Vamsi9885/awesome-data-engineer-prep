# Azure Data Factory (ADF)

## 1) What is the Service?
Azure Data Factory is Azure’s managed data integration and orchestration platform.  
It is best thought of as the **control plane** for data pipelines, not the heavy compute engine itself.

Core building blocks:
- **Pipeline**: logical workflow
- **Activity**: a step in pipeline (Copy, Databricks Notebook, Stored Proc, etc.)
- **Dataset**: named view of data source/sink
- **Linked Service**: connection info
- **Trigger**: schedule/event/tumbling window
- **Integration Runtime (IR)**: compute/network bridge (Azure, Self-hosted, SSIS)

---

## 2) When to Use?
Use ADF when you need:
- Enterprise-grade orchestration for batch workloads
- Hybrid ingestion (on-prem + cloud)
- Many connectors with minimal custom code
- Parameterized, metadata-driven pipelines
- CI/CD release process for pipelines across environments

Avoid using ADF as main transformation engine for large compute-heavy logic; offload to Databricks/Synapse/Spark.

---

## 3) Architecture Usage (Pipeline Role)
Typical role in data platform:
1. Ingest from SaaS/DB/files/API into ADLS raw zone
2. Trigger processing in Databricks/Synapse
3. Move curated data into serving stores
4. Monitor retries, failures, SLAs, lineage hooks

### Reference Batch Architecture (Azure)
`ADF (orchestration) → ADLS (raw) → Databricks (transform) → Synapse (warehouse)`

ADF responsibilities:
- dependency management
- scheduling
- retries and alerts
- secure secret usage through Key Vault

---

## 4) Real-World Example
### Amazon-like E-commerce (Batch Sales Analytics)
- Hourly order data from OLTP and partner feeds
- ADF copies data to ADLS (`raw/orders/dt=...`)
- ADF triggers Databricks job for silver/gold model
- ADF runs Synapse stored procedure for aggregate marts
- Power BI refresh triggered post-load

### Uber-like Marketplace ETL
- City-level nightly ETL for demand/supply metrics
- Tumbling window trigger ensures strict window execution
- Late-arriving files handled with watermark logic in metadata tables

### Netflix-like Content Analytics
- Daily batch of watch events from regional stores
- ADF orchestrates cross-region pulls and centralized standardization

---

## 5) Integration with Other Services
- **ADLS Gen2**: landing + zone model
- **Azure Databricks**: notebook/job execution via activity
- **Synapse**: SQL scripts / pipeline integration
- **Event Hubs**: event-driven trigger patterns (indirect)
- **Azure Functions**: custom logic or dynamic metadata fetch
- **Key Vault**: secrets and connection security
- **Monitor/Log Analytics**: observability

### Example pipeline chain
1. Copy activity: SQL Server → ADLS raw  
2. Databricks Notebook activity: raw → curated  
3. Stored Proc activity: load Synapse fact tables  
4. Webhook/Logic App: send SLA completion notification

---

## 6) Common Mistakes
1. Treating ADF as full compute engine for complex transforms
2. Hardcoding paths/parameters instead of metadata-driven configs
3. Excessive pipeline sprawl without reusable templates
4. Ignoring self-hosted IR sizing for on-prem throughput
5. Poor failure handling (no retry/backoff/dead-letter strategy)
6. Overusing data flows when Spark jobs are better suited

---

## 7) Performance Tips
- Parallelize copy with partition options and DIUs tuning
- Use binary copy for large file movement where possible
- Push heavy transforms to Databricks/Synapse
- Build metadata-driven pipelines to reduce maintenance overhead
- Use incremental loads with watermark columns
- Group small files before downstream analytics
- Use trigger windows aligned with upstream data availability

### Cost Tips
- Choose right IR type and region
- Minimize unnecessary activity runs
- Avoid over-triggering (too granular schedules)
- Use event triggers only when event volume justified

---

## 8) 🔥 Interview Questions

### Conceptual
1. **What is the difference between ADF pipeline and activity?**  
2. **What does Integration Runtime do in ADF? Why is Self-hosted IR needed?**  
3. **Why is ADF considered orchestration-first, not transformation-first?**

### Scenario-Based
4. **Your nightly load misses SLA due to increasing data volume. How do you optimize?**  
   - Partitioned copy, parallel activities, offload transform to Spark, incremental processing.
5. **How would you ingest from on-prem Oracle securely into ADLS?**  
   - Self-hosted IR, private networking, Key Vault secrets, managed identities.
6. **How do you design idempotent ADF pipelines?**  
   - watermarking, deterministic output paths, merge/upsert in sink, rerun-safe activities.

### Product/Comparison
7. **ADF vs Airflow**
   - ADF: managed connectors + enterprise integration + GUI  
   - Airflow: code-centric DAG flexibility + ecosystem portability  
   - In enterprises, many teams use **Airflow for logic orchestration** and ADF for connector-heavy ingestion.
8. **ADF vs AWS Glue Workflows vs GCP Composer**
   - ADF strongest in Azure-native integration and hybrid IR
   - Composer/Airflow strongest in Python DAG flexibility
   - Glue workflows more AWS ETL-centric than broad orchestration

### Follow-up Drill
9. **How would you build metadata-driven ADF for 500 tables?**  
10. **How to implement dynamic retries based on source type and priority?**  
11. **How do you promote ADF pipelines via CI/CD across dev/test/prod?**
