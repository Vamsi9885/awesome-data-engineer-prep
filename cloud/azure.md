# ☁️ Azure for Data Engineers

## 1. Concept Explanation

**Azure = Enterprise heavy (Flipkart, banks)**

```
Azure Mapping:
ADLS → S3/GCS
Synapse → BigQuery/Redshift
Databricks → EMR/Dataproc
Event Hubs → Kinesis/PubSub
```

**Azure Strengths:**
- Databricks native
- Power BI integration
- Enterprise security

## 2. Real-World Example - Flipkart Analytics

```
Flipkart Azure Setup:
ADLS Gen2 → Synapse → Power BI
+ Databricks (Spark/ML)
Scale: 50PB storage
```

## 3. Code Examples

### Synapse Analytics (T-SQL)
```sql
-- Flipkart sales dashboard
SELECT 
    YEAR(order_date) as year,
    MONTH(order_date) as month,
    SUM(net_amount) as revenue,
    COUNT(DISTINCT customer_id) as mau
FROM sales_fact
WHERE order_date >= '2023-01-01'
GROUP BY YEAR(order_date), MONTH(order_date);
```

### Databricks on Azure (Production)
```python
# Flipkart recommendation features
spark.read.parquet("abfss://container@flipkartadls.dfs.core.windows.net/raw/") \
    .groupBy("user_id", "product_id") \
    .agg(count("*").alias("interaction_count")) \
    .write \
    .mode("overwrite") \
    .parquet("abfss://container@flipkartadls.dfs.core.windows.net/featured/")
```

### Event Hubs Streaming
```python
# Azure Stream Analytics → Databricks
df = spark \
    .readStream \
    .format("eventhubs") \
    .option("eventhubs.connectionString", eh_conf) \
    .load()
```

## 4. Real-Time Production Scenario

**Flipkart Peak Sales (Big Billion Days):**

```
Event Hubs (orders) → Stream Analytics → 
Databricks (ML scoring) → Synapse → Power BI

Peak: 1M orders/hour
Latency: <10s end-to-end
Cost: $5K/day peak
```

## 5. Common Mistakes

| Service | Mistake | Fix |
|---------|---------|-----|
| ADLS | Public access | RBAC + firewalls |
| Synapse | Dedicated SQL | Serverless pools |
| Databricks | Classic clusters | Unity Catalog |

## 6. Azure Cost Framework

```
🏆 Azure Pricing:

Synapse: $1.20/hour (DW100c)
Databricks: $0.40/DBU + VM cost
ADLS: $0.023/GB
Event Hubs: $0.028/hour/throughput

Optimization:
1. Synapse autosuspend
2. Databricks spot instances  
3. ADLS tiering
4. Reserved capacity
```

## 7. 🔥 Interview Questions

### Flipkart L5
**Q1: ADLS vs Blob Storage?**
```
ADLS Gen2: Hierarchical namespace + ACID
Blob: Simple object storage
Use ADLS for analytics
```

**Q2: Synapse serverless vs dedicated?**
```
Serverless: Ad-hoc, pay-per-query
Dedicated: Heavy workloads, reserved
```

### Enterprise DE
**Q3: Unity Catalog benefits?**
```
A: 
1. Cross-workspace governance
2. Table/column lineage
3. Centralized access control
```

**Q4: Streaming from Event Hubs?**
```
Databricks: eventhubs format
Synapse: Stream Analytics → Synapse tables
```

### Multi-Cloud
**Q5: Migrate GCP→Azure pipeline.**
```
BigQuery → Synapse (CTAS)
GCS → ADLS (Azure Data Factory)
Dataproc → Databricks
```

**Q6: Power BI + Databricks integration.**
```
DirectQuery → Databricks SQL warehouses
OR Materialized views → Power BI datasets
```

---

**🔥 Pro Tip:** Azure Data Factory = Glue alternative (visual ETL)
```
Orchestration ≠ Processing
ADF orchestrates Databricks/Synapse
