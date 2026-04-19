# ☁️ AWS for Data Engineers

## 1. Concept Explanation

**AWS = 70% Data Engineer jobs**

```
Not "certification trivia" → Production service mapping
S3 → Storage | Glue → Catalog | EMR → Compute | Athena → Query
```

**Cost vs Performance Matrix:**
- Cheap/Slow: S3 Select
- Fast/Expensive: Redshift
- Balanced: EMR + Spark

## 2. Real-World Example - Amazon Internal Analytics

```
Amazon's own data platform:
S3 (raw) → Glue (catalog) → EMR (processing) → 
Athena (ad-hoc) → QuickSight (dashboards)
```

## 3. Code Examples

### Complete AWS Pipeline (Terraform + PySpark)
```hcl
# Infrastructure
resource "aws_glue_catalog_database" "ecommerce" {
  name = "ecommerce_db"
}

resource "aws_s3_bucket" "raw" {
  bucket = "amazon-ecommerce-raw"
}
```

```python
# PySpark on EMR
spark.read.parquet("s3://amazon-ecommerce-raw/orders/") \
    .write.format("parquet") \
    .partitionBy("dt") \
    .save("s3://amazon-ecommerce-curated/")
```

### Athena Partition Management
```sql
-- Add new partitions (automated)
MSCK REPAIR TABLE orders;

-- Or explicit
ALTER TABLE orders ADD 
PARTITION (dt='2024-01-15') 
LOCATION 's3://.../dt=2024-01-15/';
```

## 4. Real-Time Production Scenario

**Flipkart Black Friday Pipeline:**

```
Peak: 10M orders/hour
1. Kinesis → Bronze S3 (raw JSON)
2. Glue streaming ETL → Silver Parquet  
3. Athena materialized views → Gold
4. QuickSight dashboards

Cost: $2K/day peak (optimized)
Scale: Auto-scaling EMR
```

## 5. Common Mistakes

| Service | Mistake | Cost Impact |
|---------|---------|-------------|
| S3 | No partitioning | 100x scan cost |
| Glue | Dynamic frames | 5x slower |
| EMR | Spot + On-demand | 3x cost |
| Athena | SELECT * | $100/query |

## 6. Cost Optimization Framework

```
🏆 AWS DE Cost Matrix ($/TB processed):

S3 Select:     $0.40 (slow)
Athena:        $5.00 (ad-hoc) 
EMR Spark:     $2-10 (batch)
Redshift:     $50+ (OLAP)
Glue:         $15/hr (ETL)

Optimization Rules:
1. S3 partitioning > Athena CTAS
2. EMR spot instances (70% savings)  
3. Glue job bookmarks
4. Athena materialized views
```

## 7. 🔥 Interview Questions

### Amazon L5
**Q1: 1TB daily processing. Cheapest architecture?**
```
A: 
S3 (Intelligent Tiering) → EMR (spot r5.2xlarge) → 
Athena (partitioned tables)
Cost: ~$3/TB vs Redshift $50/TB
```

**Q2: Glue vs EMR?**
```
Glue: Serverless, simple ETL
EMR: Custom Spark, ML, large scale
```

### Uber L4 (AWS Heavy)
**Q3: S3 costs high. Optimize.**
```
A: 
1. Partitioning (dt/city)
2. Parquet compression
3. S3 Intelligent Tiering
4. Athena partition projection
```

**Q4: Streaming pipeline?**
```
Kinesis → Spark Streaming (EMR) → 
S3 (optimized writes) → Athena
```

### Flipkart Production
**Q5: EMR cluster sizing?**
```
A: 
r5.2xlarge (8c/64G) x 20 core nodes
1 driver + 19 executors
Shuffle partitions: 400
Executor memory: 14G
```

**Q6: Athena slow queries.**
```
A: 
1. Partition projection
2. CTAS to new tables  
3. Columnar stats
4. Workgroups + budgets
```

---

**💰 Pro Tip:** AWS Cost Explorer + CloudWatch = your DE dashboard
```
Budget: $10K/month
Alert: >$300/day
