# ⚠️ Data Skew Handling in PySpark (Debugging + Fix Playbook)

---

## 1) Concept Explanation

**Data skew** means key/value distribution is imbalanced, causing some partitions/tasks to process far more data than others.

Symptoms:
- One/few tasks run much longer (stragglers)
- Stage appears “stuck at 99%”
- High spill/OOM on specific executors
- Poor cluster utilization (many executors idle)

Skew is a top reason for slow joins and aggregations in production Spark jobs.

---

## 2) Causes of Skew

1. Hot keys (e.g., `country='US'`, `merchant_id=123`)
2. Low-cardinality join/groupBy keys
3. Null-heavy keys joining together
4. Bad partitioning strategy
5. Time-based burst concentration (event spikes in few windows)

---

## 3) Impact on Jobs

- Long tail latency
- Higher spill to disk
- Retry/failure risk
- SLA misses and cloud cost increase

In interviews, mention both **performance impact** and **stability impact**.

---

## 4) PySpark Code Examples (Real-World)

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, concat_ws, rand, floor, broadcast

spark = SparkSession.builder.appName("skew-handling").getOrCreate()
```

### A) Detect skew quickly

```python
# Top keys by volume
df.groupBy("customer_id").count().orderBy(col("count").desc()).show(20, truncate=False)
```

### B) Salting for skewed joins

```python
# Large skewed fact
orders = spark.read.parquet("s3://lake/orders/")
# Smaller dim
customers = spark.read.parquet("s3://lake/dim/customers/")

salt_buckets = 10

orders_salted = orders.withColumn(
    "salt",
    floor(rand(seed=42) * salt_buckets)
).withColumn(
    "join_key",
    concat_ws("_", col("customer_id").cast("string"), col("salt").cast("string"))
)

# Replicate dim rows across salt buckets
salt_values = spark.range(0, salt_buckets).toDF("salt")
customers_salted = customers.crossJoin(salt_values).withColumn(
    "join_key",
    concat_ws("_", col("customer_id").cast("string"), col("salt").cast("string"))
)

joined = orders_salted.join(customers_salted, "join_key", "left")
```

### C) Broadcast join to avoid heavy shuffle (when dim is small)

```python
joined_fast = orders.join(broadcast(customers.select("customer_id", "segment")), "customer_id", "left")
```

### D) Repartition by better key

```python
balanced = orders.repartition(400, "customer_id")
```

---

## 5) DAG Explanation

Skewed join path without mitigation:

```text
Stage 1: read fact + read dim
Stage 2: shuffle both by join key
Stage 3: one reduce partition gets huge hot key -> straggler task
```

With salting:

```text
Stage 1: add salt keys
Stage 2: shuffle on salted key (hot key split across buckets)
Stage 3: join workload distributed more evenly
```

---

## 6) Spark Internals (Basic → Moderate)

Where skew hurts internally:
- shuffle partition files become uneven
- one task fetches huge shuffle blocks
- execution memory pressure rises, causing spill/OOM

How Spark helps:
- AQE skew optimization can split skewed partitions at runtime.
- Spark UI highlights skew through task runtime and shuffle size variance.

Useful configs:
```python
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
```

Inspect with:
```python
df.explain("formatted")
```
and Spark UI:
- Stage task duration distribution
- shuffle read per task
- spilled bytes per task

---

## 7) Real-World Scenario

**Ride-sharing surge analytics (Uber-like)**  
Problem:
- Join of trips with city-pricing map skewed on mega-city IDs.
- One task 20x longer; micro-batch SLAs breached.

Fix:
1. Broadcasted static city-pricing table (small enough)
2. Applied salting on mega-city hot keys for larger historical joins
3. Enabled AQE skew handling
4. Added key distribution checks in pre-flight validation

Result:
- P95 stage time reduced by ~65%
- no executor OOM during peak windows

---

## 8) Common Mistakes

1. Treating skew as “cluster too small” and only scaling hardware.
2. Applying salting blindly to all keys (can add unnecessary complexity).
3. Forgetting to replicate dimension keys when salting join.
4. Ignoring null-key skew.
5. Over-partitioning without understanding key distribution.
6. Not validating fixes in Spark UI metrics.

---

## 9) Performance Tips

- Profile key distribution before joins/groupBy.
- Filter data early and drop unnecessary columns pre-shuffle.
- Broadcast genuinely small dimensions.
- Use salting only for confirmed hot keys.
- Enable AQE skew handling.
- Consider separating hot keys into dedicated pipeline branch.
- Keep output file sizes balanced after skew fixes.

---

## 10) 🔥 Interview Questions

## Basic
1. What is data skew in Spark?
2. How do you detect skew?
3. Why does skew hurt job performance?

## Advanced
1. Explain salting and when to use it.
2. How does AQE handle skewed joins?
3. Skew in joins vs skew in aggregations: differences in mitigation?
4. How do you validate skew fixes scientifically?

## Product Scenarios
1. Stage stuck at 99% due to one task. Walk through diagnosis and fix.
2. Fact table has one key with 30% of records. Join strategy?
3. Streaming pipeline has skew at specific hourly windows. How to stabilize latency?

## Follow-up Questions
- Can broadcast join fully solve skew?
- What are downsides of salting?
- How do nulls contribute to skew?
- When would you split hot keys into separate flow?

---

## 11) Quick Fix Decision Tree

```text
If dim small? -> Broadcast join.
Else if few hot keys? -> Salt hot keys only.
Else if broad imbalance? -> Repartition + AQE skew handling.
Always -> Validate in Spark UI (task time, shuffle size, spill).
```

---

## 12) Global Cross-Coverage

- **How to identify skew?**  
  Task duration outliers + skewed key counts + uneven shuffle read.
- **How to fix skew in joins?**  
  Broadcast, salting, key-based repartitioning, AQE skew split.
- **How does Spark handle failures in skew scenarios?**  
  Task retries occur, but retries don’t solve distribution imbalance; logic-level fix is required.
