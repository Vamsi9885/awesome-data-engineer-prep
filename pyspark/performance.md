# 🚀 PySpark Performance Tuning

## 1. Concept Explanation

**90% of Spark jobs fail on performance, not correctness**

```
Default config: 1 job/hour
Tuned config: 100 jobs/hour
Wrong config: OOM/crash/cost explosion
```

**3 Layers of Tuning:**
1. **Code** (70% impact)
2. **Config** (20% impact) 
3. **Cluster** (10% impact)

## 2. Real-World Example - Netflix Content Pipeline

```
Before: 6hr daily batch → Miss SLA
After: 45min batch → Headroom for ad-hoc

Cost: $300/day → $45/day (87% savings)
```

## 3. Code Examples

### Shuffle Reduction (BIGGEST lever)
```python
# ❌ BAD: Massive shuffle
df.groupBy("city").agg(sum("revenue"))

# ✅ GOOD: Pre-aggregate
df_filtered = df.filter(col("date") >= "2024-01-01")
df_preagg = df_filtered.groupBy("city").agg(sum("revenue").alias("daily_rev"))
df_preagg.repartition(10).write.parquet("...")

# Repartition strategy
df.repartition(200, "date", "region")  # Better hash distribution
df.coalesce(50)  # Reduce AFTER aggregations
```

### Caching Strategy
```python
# Cache expensive transformations only
df_clean.persist(pyspark.StorageLevel.MEMORY_AND_DISK)  # Spill to disk if needed

# Unpersist when done
df_clean.unpersist()
```

### Broadcast Anti-Pattern Fix
```python
# Check sizes first!
print("Small DF:", df_drivers.count())  # 10K rows
print("Large DF:", df_trips.count())    # 100M rows

df_trips.join(broadcast(df_drivers), "driver_id")
```

## 4. Real-Time Production Scenario

**Swiggy Peak Hour Processing (10M orders/hour):**

```
Cluster: 100 r5.4xlarge (EMR)
Input: S3 → 50TB/day
Peak load: 300K orders/min

Tuning applied:
1. AQE + skew join hints
2. Dynamic allocation
3. Bucketed tables
4. Predicate pushdown

Result: P99 latency < 2min
```

## 5. Common Mistakes

| Mistake | Spark UI Symptom | Fix |
|---------|------------------|-----|
| `collect()` | Driver OOM | Never! |
| No partitioning | 1 shuffle block | Repartition |
| UDF explosion | Task 10x slower | Native functions |
| Wrong join order | Cartesian | Broadcast small |

## 6. Performance Checklist

```
🏆 Spark Tuning Framework (Production):

SPARK CONFIG (set these ALWAYS):
```python
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true") 
spark.conf.set("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
spark.conf.set("spark.sql.shuffle.partitions", "200")
spark.conf.set("spark.executor.memory", "8g")
```

SPARK UI CHECKLIST:
✅ Green tasks (no skew)
✅ No spill to disk  
✅ Shuffle read < 2GB/partition
✅ Executors >80% utilized
```

## 7. 🔥 Interview Questions

### Amazon L6 (Senior DE)
**Q1: Job slow at 6hr. Spark UI shows skew.**
```
A: 
1. salting: driver_id + random()
2. repartition(400, "driver_id")
3. AQE skew hint: /*+ SKEW('trips', 12345) */
```

**Q2: OOM during join. Fix.**
```
A: 
1. broadcast if <10MB
2. bucketed join (pre-cluster)
3. AQE (auto broadcast)
```

### Uber L5
**Q3: 100TB deduplication strategy?**
```python
# APPROACH:
window = Window.partitionBy("trip_id").orderBy("event_time")
df_dedup = df.withColumn("rn", row_number().over(window)) \
             .filter(col("rn") == 1)
```

**Q4: Shuffle partitions too high/low?**
```
A: Rule: 128MB-1GB per partition
   Monitor: Spark UI → Shuffle Read Size
```

### Flipkart Production
**Q5: EMR cluster underutilized (30%).**
```
A: 
1. Dynamic allocation
2. Reduce shuffle partitions
3. Increase parallelism (repartition)
```

**Q6: Streaming job backpressure.**
```
A: 
1. Increase watermark
2. Reduce state size  
3. Multiple streaming queries
```

---

**🔥 Pro Tip:** Never tune without Spark UI. It's your production dashboard.
```
http://driver:2088  # Bookmark this!
