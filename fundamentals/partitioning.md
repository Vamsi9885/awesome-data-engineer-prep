# 🗂️ Partitioning Strategies

## 1. Concept Explanation

**Partitioning = Query Speed Multiplier**

```
Without partitioning: Full table scan
With partitioning: Prune 99% of data

Reality: 1TB table → 1GB scan (1000x improvement)
```

**Types:**
- **Hive-style**: Directory-based (date=2024/city=blr)
- **Z-order**: Multi-dimensional clustering
- **Sort keys**: Single dimension optimization

## 2. Real-World Example - Flipkart Orders

```
Flipkart Orders (100M/day):
Table Size: 50TB
Query: "Orders from Bangalore yesterday"

❌ No partitioning: Scan 50TB
✅ Date + City: Scan 50GB (1000x faster)
```

## 3. Code Examples

### Hive Partitioning (Most Common)
```sql
-- Create partitioned table
CREATE TABLE orders (
    order_id BIGINT,
    customer_id BIGINT,
    amount DECIMAL(10,2)
)
PARTITIONED BY (dt STRING, city STRING)
STORED AS PARQUET;

-- Insert with partition
INSERT INTO orders PARTITION (dt='2024-01-15', city='blr')
SELECT order_id, customer_id, amount FROM staging;
```

### PySpark Dynamic Partitioning
```python
df.write \
  .partitionBy("dt", "city") \
  .mode("overwrite") \
  .parquet("s3://flipkart/orders/")

# Result: s3://flipkart/orders/dt=2024-01-15/city=blr/
```

### Athena Partition Projection (Serverless)
```sql
CREATE TABLE orders (
    order_id BIGINT,
    amount DECIMAL(10,2)
)
PARTITIONED BY (dt string, city string)
LOCATION 's3://flipkart/orders/'
TBLPROPERTIES (
  'projection.enabled'='true',
  'projection.dt.range'='2023-01-01/NOW',
  'projection.city.values'='blr,del,mum,hyd,pune'
);
```

## 4. Real-Time Production Scenario

**Amazon Seller Analytics (1B records/day):**

```
1. Raw Kinesis → S3 (hourly Parquet)
2. Glue Crawler → Partition discovery
3. Athena queries → Partition pruning
4. QuickSight → Seller dashboards

Query time: 5min → 3s (100x improvement)
Cost: $5 → $0.05 (100x savings)
```

## 5. Common Mistakes

| Mistake | Impact | Fix |
|---------|--------|-----|
| Too many partitions (1M+) | Metadata explosion | Max 10K partitions |
| High-cardinality (user_id) | No pruning | Low-cardinality (date, region) |
| Static partitions | Manual maintenance | Dynamic partitioning |
| Small files per partition | S3 GET costs | File compaction |

## 6. Performance Tips

```
🏆 Partitioning Tier List:

S-Tier: date (daily) + region (10-50 values)
A-Tier: category (100 values max)
B-Tier: hour (24 values)
F-Tier: user_id, order_id, email

Z-Order Magic (Databricks):
```python
df.write \
  .option("zOrderBy", "customer_id,amount") \
  .parquet("...")
```
```

**Partition Sizing Rule:** 100MB-1GB per partition

## 7. 🔥 Interview Questions

### Amazon L5
**Q1: Design partitioning for 1B daily Amazon orders**
```
A: dt (daily), marketplace_id (10), category (50)
MAX: 10K * 100MB = 1TB metadata safe
Z-order: customer_id within partitions
```

**Q2 Follow-up: Partition pruning not working?**
```
A: 
1. Check partition column types match
2. Use exact values (no LIKE %)
3. Refresh metadata (MSCK REPAIR)
```

### Uber L4
**Q3: 10TB ride table, city filter slow. Fix?**
```
A: 
1. Partition: dt, city (not user_id)
2. Sort: pickup_time within partition
3. Z-order: lat, lng
4. Compact small files
```

**Q4: Dynamic vs static partitioning?**
```
A: Dynamic = auto folder creation
   Static = explicit PARTITION clause
   Use dynamic for streaming
```

### Swiggy Scenario
**Q5: Costs exploded after partitioning. Why?**
```
A: Small files (1MB each) → 1M S3 objects
   Fix: File compaction to 128MB
```

**Q6: Best partition for time-series IoT data?**
```
A: year/month/day/hour (4-level)
   Avoid minute/second (too granular)
```

---

**⚡ Pro Tip:** Always test partition pruning with EXPLAIN!
```sql
EXPLAIN SELECT * FROM orders WHERE dt='2024-01-15';
-- Look for: "partition prune"
