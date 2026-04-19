# 🔄 PySpark Transformations (Execution + Internals + Interview)

---

## 1) Concept Explanation

A **transformation** creates a new DataFrame/RDD from an existing one, but does not execute immediately (lazy).

Two categories matter most in interviews:

- **Narrow transformation**: child partition depends on one parent partition (no shuffle).
- **Wide transformation**: data movement across partitions required (shuffle).

Examples:
- Narrow: `select`, `filter`, `withColumn`, `map`
- Wide: `groupBy`, `distinct`, `repartition`, non-broadcast `join`

Why this matters:
- Narrow ops scale linearly and are cheaper.
- Wide ops add stage boundaries and expensive shuffle.

---

## 2) PySpark Code Examples (Real-World)

### Example A: Narrow-heavy log cleanup

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp, lower, trim

spark = SparkSession.builder.appName("log-cleanup").getOrCreate()

logs = spark.read.json("s3://company/raw/logs/")

clean = (
    logs
    .select("event_id", "service", "level", "message", "event_ts")
    .filter(col("event_id").isNotNull())
    .withColumn("service", lower(trim(col("service"))))
    .withColumn("event_time", to_timestamp("event_ts"))
)
```

This chain is mostly narrow transformations.

### Example B: Wide transformation with groupBy

```python
from pyspark.sql.functions import count

error_counts = (
    clean
    .filter(col("level") == "error")
    .groupBy("service")       # wide transformation -> shuffle
    .agg(count("*").alias("error_count"))
)
```

### Example C: join as wide transformation (unless broadcast)

```python
service_dim = spark.read.parquet("s3://company/dim/service_catalog/")

joined = error_counts.join(service_dim, "service", "left")
```

---

## 3) DAG Explanation

For `clean -> groupBy -> join -> write`:

```text
Stage 1:
  read logs -> select -> filter -> withColumn (narrow chain)

Stage 2:
  groupBy(service) + agg(count)              (shuffle boundary)

Stage 3:
  join with service_dim (depends on strategy:
   - shuffle join => another wide stage
   - broadcast join => avoids large shuffle)

Stage 4:
  write output
```

Lazy evaluation means Spark constructs this DAG first and executes on action.

---

## 4) Spark Internals (Basic → Moderate)

- Transformations on DataFrame build a **logical plan**.
- Catalyst applies rule-based and cost-aware optimizations.
- Physical operators selected:
  - `ProjectExec`, `FilterExec` for narrow ops
  - `HashAggregateExec`, `SortMergeJoinExec` etc. for wide ops
- Stage split occurs at `Exchange` operators (shuffle boundary).
- AQE may alter physical plan at runtime (e.g., convert SMJ to Broadcast Hash Join).

Inspect:
```python
joined.explain("formatted")
```

Look for:
- `Exchange` (shuffle)
- join type
- scan pushdowns

---

## 5) Real-World Scenario

**Ad-tech hourly pipeline (batch + near-real-time):**
- 2 TB/hour impressions
- Transformations:
  - Narrow: parse, schema validation, enrichment flags
  - Wide: dedup by user-window, groupBy campaign, joins with dimensions
- Production strategy:
  - Keep narrow transformations before wide transformations
  - Reduce row width before shuffle (select only required columns)
  - Broadcast small dimensions to avoid second shuffle stage

---

## 6) Common Mistakes

1. Writing transformation code assuming each line runs immediately.
2. Doing expensive UDF transform before filtering.
3. Running `distinct` early on full-width rows (massive shuffle).
4. Multiple unnecessary `repartition()` calls.
5. Joining before reducing data volume (filter/project first).

---

## 7) Performance Tips

- Push `filter` and `select` as early as possible.
- Combine transformations to avoid materializing intermediate outputs.
- Prefer built-in functions over Python UDFs.
- For wide ops:
  - tune partition count,
  - handle skew keys,
  - broadcast small dimensions.
- Use `explain()` and Spark UI together to validate assumptions.

---

## 8) 🔥 Interview Questions

## Basic
1. What is a transformation in Spark?
2. Why are transformations lazy?
3. Difference between narrow and wide transformations?
4. Give examples of each.

## Advanced
1. How does Spark decide stage boundaries?
2. Why can `groupBy` become a bottleneck?
3. What does `Exchange` operator represent in physical plan?
4. How can AQE change transformation execution at runtime?

## Product Scenarios
1. A pipeline slowed after adding `distinct()`. Diagnose likely root cause.
2. You have multiple joins + aggregations. How do you order transformations?
3. Where would you place data quality checks to minimize compute cost?

## Follow-up Questions
- Is `withColumn` always cheap?
- Is `join` always wide?
- Can two wide transformations be in same stage?
- When to use `repartition` vs leave as-is?

---

## 9) Quick Interview Cheat Sheet

```text
Narrow = no shuffle, cheap, pipelined in same stage.
Wide   = shuffle, expensive, new stage boundary.
Lazy   = Spark plans first, executes only on action.
Rule   = Filter/Project early, shuffle late, broadcast small, inspect plan.
