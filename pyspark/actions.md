# ▶️ PySpark Actions (How Execution Gets Triggered)

---

## 1) Concept Explanation

An **action** is an operation that forces Spark to execute the lazy transformation DAG and produce:
- data on driver (`collect`, `take`, `show`)
- scalar results (`count`)
- external side effects (`write`, `saveAsTable`)

Without an action, transformations remain a plan only.

Common actions:
- `count()`
- `show()`
- `collect()`
- `take(n)`
- `first()`
- `foreach()`
- `write...`

---

## 2) PySpark Code Examples (Real-World)

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

spark = SparkSession.builder.appName("actions-demo").getOrCreate()

df = spark.read.parquet("s3://warehouse/orders/") \
    .filter(col("order_date") >= "2024-01-01") \
    .filter(col("status") == "COMPLETE")
```

### `count()` action
```python
total = df.count()
print(total)
```

### `show()` action
```python
df.select("order_id", "customer_id", "amount").show(20, truncate=False)
```

### `collect()` action (dangerous for big data)
```python
small = df.limit(100).collect()  # safe only if bounded and tiny
```

### `write` action
```python
df.write.mode("overwrite").parquet("s3://warehouse/marts/orders_complete/")
```

---

## 3) DAG Explanation

For:
`read -> filter -> filter -> select -> write`

```text
Before action:
  logical/physical plan exists, no tasks executed.

Action called (write/count/show):
  Job created
    -> Stage(s) split at shuffle boundaries
    -> Task per partition sent to executors
    -> Result to sink/driver
```

If no wide transformation, there may be a single stage pipeline.
If `groupBy/join/distinct` exists, shuffle adds additional stages.

---

## 4) Spark Internals (Basic → Moderate)

What happens internally when action is called:

1. Driver finalizes optimized physical plan (Catalyst).
2. DAG Scheduler builds stages.
3. Task Scheduler assigns partition tasks to executors.
4. Executors process data, spill/shuffle if needed.
5. Action result:
   - For `count`: partial counts aggregated, scalar returned.
   - For `show`: subset collected to driver for display.
   - For `write`: tasks write partition outputs to sink.

Important internals:
- Each action can trigger a new job.
- Repeated actions on same lineage recompute unless cached.
- AQE can adjust plan after seeing runtime stats.

---

## 5) Real-World Scenario

**Databricks ETL validation pattern**
- Transformations build cleaned silver DataFrame.
- Actions used:
  1. `count()` for quality gate (row thresholds)
  2. `write.format("delta")...` for final persist
  3. Optional `show(10)` in debug notebook only

Production rule:
- Never `collect()` full DataFrame in scheduled jobs.
- Keep driver memory protected from large result pulls.

---

## 6) Common Mistakes

1. Using `collect()` on millions of rows (driver OOM).
2. Calling multiple actions (`count`, `show`, `write`) repeatedly without caching.
3. Using `show(100000)` in debugging notebooks.
4. Assuming actions are cheap because code is short.
5. Triggering expensive actions in loops.

---

## 7) Performance Tips

- Prefer `write` to storage over `collect` to driver.
- Use `take(n)` / `limit(n).toPandas()` only for tiny sample validation.
- Cache if same DataFrame is used by multiple actions:
  ```python
  df.cache()
  df.count()
  df.write.parquet("...")
  ```
- Use `explain()` before action to inspect join/shuffle choices.
- Monitor Spark UI jobs/stages to locate action bottlenecks.

---

## 8) 🔥 Interview Questions

## Basic
1. What is an action in Spark?
2. How do actions differ from transformations?
3. Why do transformations not execute immediately?
4. Name common Spark actions.

## Advanced
1. What happens internally when `count()` is called?
2. Why can two actions on same DataFrame be expensive?
3. How does Spark decide number of tasks for an action?
4. Why is `collect()` dangerous?

## Product Scenarios
1. A job OOMs only during final step. Code uses `collect()`. How would you fix?
2. A notebook runs `count()` then `write()` on same heavy DataFrame; optimize it.
3. How would you validate output quality without expensive repeated actions?

## Follow-up Questions
- Is `show()` always safe?
- Does `write` trigger a job?
- Can `limit(10).collect()` still scan large data?
- When would you use `foreachPartition`?

---

## 9) Interview Must-Know: collect() Danger

`collect()` pulls all partitions to the driver process.
- Executor memory may be fine, driver crashes.
- Network transfer spikes.
- Notebook freezes or kernel dies.

Safer alternatives:
- `show(20)`
- `limit(1000).toPandas()`
- write sampled output to storage

---

## 10) Global Interview Cross-Links

- **Why Spark is faster than Hadoop?**  
  In-memory execution + DAG optimization + codegen, unlike strict map/reduce materialization at every phase.
- **How Spark handles failures?**  
  Task retries + lineage recomputation + speculative execution.
- **What happens during shuffle?**  
  Partition exchange over network + disk spill + merge/sort on reduce side.
