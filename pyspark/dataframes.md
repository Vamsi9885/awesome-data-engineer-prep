# ⚡ PySpark DataFrames Mastery

## 1. Concept Explanation

**DataFrame = SQL on Spark (Distributed)**

```
Pandas: 1 machine, 10GB RAM → OOM
DataFrame: 1000 machines, 10TB data → Fine

SQL on DataFrame = 10x faster than RDD
```

**Key Abstraction:**
- Schema enforcement
- Catalyst optimizer
- Tungsten execution
- WholeStage codegen

## 2. Real-World Example - Uber Trip Processing

```
Uber Daily Pipeline:
Raw: 50M trips (JSON)
→ DataFrame (schema enforced) 
→ Cleaned (10GB Parquet)
→ Aggregated (dashboard)
→ 45min end-to-end
```

## 3. Code Examples

### Production Pipeline Template
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

spark = SparkSession.builder \
    .appName("UberTrips") \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
    .getOrCreate()

# 1. Read with schema (CRITICAL!)
schema = "trip_id STRING, driver_id LONG, fare DOUBLE, trip_date DATE"
df = spark.read.schema(schema).parquet("s3://uber/trips/raw/")

# 2. Production transformations
df_clean = df.filter(col("fare") > 0) \
    .withColumn("trip_month", month("trip_date")) \
    .withColumn("revenue_net", col("fare") * 0.8)  # Uber's 20% cut

# 3. Write optimized
df_clean.coalesce(10) \
    .write.mode("overwrite") \
    .partitionBy("trip_month") \
    .parquet("s3://uber/trips/clean/")
```

### Common Operations (Interview Must-Know)
```python
# Joins (broadcast small tables!)
df_large.join(broadcast(df_drivers), "driver_id")

# Window functions
from pyspark.sql.window import Window
window_spec = Window.partitionBy("driver_id").orderBy("trip_date")
df.withColumn("rank", rank().over(window_spec))

# UDFs (avoid if possible!)
@udf(returnType=DoubleType())
def calculate_distance(lat1, lon1, lat2, lon2):
    # Haversine formula
    pass
```

## 4. Real-Time Production Scenario

**Amazon Kinesis → Spark Streaming (1M events/sec):**

```
1. Kinesis JSON → DataFrame (schema registry)
2. Watermark + Window aggregation
3. State store (RocksDB)
4. Kafka output (exactly-once)

Spark UI metrics:
- Input: 1M/sec
- Processing: 900K/sec
- Latency: P99 < 5s
```

## 5. Common Mistakes

| Mistake | Symptom | Fix |
|---------|---------|-----|
| `collect()` | Driver OOM | `write()` |
| No schema | Schema inference | Explicit schema |
| `toPandas()` | 10GB RAM crash | Sample first |
| UDF heavy | 10x slowdown | Built-in functions |

## 6. Performance Tips

```
🏆 Spark DataFrame Optimization:

1. Cache/persist strategic DataFrames
2. Broadcast joins (<10MB tables)
3. Adaptive Query Execution (AQE)
4. Bucketed tables (join optimization)
5. Predicate pushdown

Spark UI Red Flags:
❌ Spill to disk     <- Increase executor memory
❌ Task skew        <- Salting/repartition  
❌ 2000 tasks       <- coalesce(50)
```

**Config for Production:**
```python
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", "true")
```

## 7. 🔥 Interview Questions

### Amazon L5
**Q1: 10TB trips slow. Optimize.**
```python
# Fix:
df = spark.read.parquet("s3://...") \
    .filter(col("trip_date") >= lit("2024-01-01"))  # Pushdown!
df.repartition(200, "driver_id") \
    .cache()  # Reuse multiple times
```

**Q2: Join slow?**
```
A: df_large.join(broadcast(df_small), "id")
   Check: spark.sql.autoBroadcastJoinThreshold
```

### Uber L4
**Q3: Pipeline OOMs at 50GB. Fix.**
```python
# Solutions:
df.coalesce(50)  # Reduce shuffle partitions
df.repartition(100, "date")  # Better distribution
spark.conf.set("spark.sql.shuffle.partitions", "200")
```

**Q4: UDF vs built-in?**
```
A: Always built-in (vectorized)
spark.sql("SELECT distance_udf(lat, lon)")  # Slow!
```

### Flipkart Streaming
**Q5: Exactly-once processing?**
```
A: Checkpointing + Idempotent writes
df.write \
  .format("delta") \
  .option("checkpointLocation", "/checkpoints") \
  .mode("overwrite") \
  .save()
```

**Q6: Spark UI shows spill. Fix?**
```
A: Increase executor memory
   OR Reduce partition size
   OR Use AQE (coalesce post-shuffle)
```

---

**⚡ Pro Tip:** Spark UI = your best friend. Live metrics > theory every time.
