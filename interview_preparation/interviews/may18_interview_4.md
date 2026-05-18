# 🔥 Databricks & Spark Interview Prep — 27 Real Questions & Answers

> Questions from a real Data Engineer interview covering Delta Lake, AQE, Broadcast Joins, Z-Ordering, Bloom Filters, and PySpark UDF optimization.

---

## 📌 Section 1: Data Quality & Delta Lake Fundamentals

---

### Q1. What are data quality checks in Databricks?

Data quality checks ensure that data ingested or transformed in pipelines meets defined standards for accuracy, completeness, consistency, and validity.

**Common types:**
- **Null checks** – Ensure critical columns are not null
- **Uniqueness checks** – Detect duplicate records
- **Schema validation** – Enforce expected column types and names
- **Referential integrity** – Validate foreign key relationships
- **Range/threshold checks** – Ensure numeric values fall within expected bounds
- **Freshness checks** – Validate data is not stale

**Tools in Databricks:**
- **Delta Live Tables (DLT) Expectations** – Declarative quality rules with `EXPECT`, `EXPECT OR DROP`, `EXPECT OR FAIL`
- **Great Expectations** – Open-source framework integrated with Databricks
- **Custom PySpark assertions** – Manual row-level validation logic

```python
# DLT Example
@dlt.table
@dlt.expect("valid_user_id", "user_id IS NOT NULL")
@dlt.expect_or_drop("positive_amount", "amount > 0")
def clean_transactions():
    return spark.read.table("raw_transactions")
```

---

### Q2. How do you implement data quality validations in Databricks pipelines?

**Approach 1: Delta Live Tables (DLT) Expectations**
```python
import dlt

@dlt.table
@dlt.expect_all({
    "valid_id": "id IS NOT NULL",
    "non_negative_amount": "amount >= 0",
    "valid_status": "status IN ('ACTIVE', 'INACTIVE')"
})
def validated_orders():
    return dlt.read("raw_orders")
```

**Approach 2: Custom PySpark Validation**
```python
def validate_dataframe(df, rules: dict):
    failed_records = {}
    for rule_name, condition in rules.items():
        failed = df.filter(f"NOT ({condition})")
        count = failed.count()
        if count > 0:
            failed_records[rule_name] = count
            print(f"[FAIL] {rule_name}: {count} records violated")
    return failed_records

rules = {
    "no_null_user_id": "user_id IS NOT NULL",
    "valid_amount": "amount BETWEEN 0 AND 100000"
}
validate_dataframe(df, rules)
```

**Approach 3: Great Expectations on Databricks**
- Define expectation suites
- Integrate with Delta tables as checkpoints
- Publish validation results to a data docs site

**Best Practices:**
- Log bad records to a quarantine/dead-letter table
- Set severity levels: warn vs. fail
- Track data quality metrics over time in a monitoring dashboard

---

### Q3. What are the key features of Delta Lake tables?

| Feature | Description |
|---|---|
| **ACID Transactions** | Full atomicity, consistency, isolation, durability on data lakes |
| **Schema Enforcement** | Rejects writes that don't match the table schema |
| **Schema Evolution** | `mergeSchema` option allows adding/changing columns |
| **Time Travel** | Query historical versions using `VERSION AS OF` or `TIMESTAMP AS OF` |
| **MERGE (Upsert)** | Native MERGE INTO for SCD, CDC, and deduplication |
| **Z-Ordering** | Multi-dimensional clustering for faster file pruning |
| **Data Skipping** | Min/max statistics stored per file for query optimization |
| **Compaction (OPTIMIZE)** | Merges small files into larger ones for performance |
| **Vacuum** | Cleans up old data files beyond retention threshold |
| **Change Data Feed (CDF)** | Tracks row-level changes (insert/update/delete) |
| **Bloom Filters** | Probabilistic index for high-cardinality column lookups |
| **Liquid Clustering** | Next-gen alternative to partitioning + Z-Ordering (Databricks) |

---

### Q4. What is Time Travel in Delta Lake?

Time Travel is the ability to query **historical versions** of a Delta table — either by version number or timestamp — without maintaining separate snapshot tables.

Delta Lake stores transaction logs (JSON files) in the `_delta_log` directory. Every write creates a new version. Time Travel reads the state of the table at a specific version or point in time.

**Use cases:**
- Audit and compliance (who changed what, when)
- Debugging bad data loads
- Rolling back accidental deletes/updates
- Reproducible ML training datasets

**Retention:** Controlled by `delta.logRetentionDuration` (default: 30 days) and `delta.deletedFileRetentionDuration` (default: 7 days).

---

### Q5. How can you perform Time Travel in Spark using Delta tables?

**By Version Number:**
```python
# PySpark
df = spark.read.format("delta") \
    .option("versionAsOf", 5) \
    .load("/delta/events")

# SQL
SELECT * FROM events VERSION AS OF 5;
```

**By Timestamp:**
```python
# PySpark
df = spark.read.format("delta") \
    .option("timestampAsOf", "2024-01-15 00:00:00") \
    .load("/delta/events")

# SQL
SELECT * FROM events TIMESTAMP AS OF '2024-01-15 00:00:00';
```

**RESTORE a table to a previous version:**
```sql
RESTORE TABLE events TO VERSION AS OF 10;
RESTORE TABLE events TO TIMESTAMP AS OF '2024-01-10';
```

**View history:**
```sql
DESCRIBE HISTORY events;
```

---

### Q6. Can Time Travel be implemented in Snowflake? How does it differ from Delta Lake?

Yes, Snowflake supports Time Travel natively.

| Aspect | Delta Lake | Snowflake |
|---|---|---|
| **Mechanism** | Transaction log + Parquet snapshots | Automatic storage of historical data |
| **Syntax** | `VERSION AS OF`, `TIMESTAMP AS OF` | `AT (VERSION => N)`, `AT (TIMESTAMP => ...)`, `BEFORE (STATEMENT => query_id)` |
| **Retention** | Default 30 days (configurable) | 0–90 days (Enterprise: up to 90 days) |
| **RESTORE** | `RESTORE TABLE` command | `CREATE TABLE ... CLONE ... AT (...)` |
| **Cost** | Storage cost for old Parquet files | Snowflake charges for Time Travel storage |
| **Fail-safe** | No built-in fail-safe | 7-day fail-safe period beyond Time Travel |
| **Control** | You manage retention yourself | Snowflake manages retention automatically |

**Snowflake Time Travel Example:**
```sql
-- Query 3 days ago
SELECT * FROM orders AT (TIMESTAMP => DATEADD(days, -3, CURRENT_TIMESTAMP));

-- Query before a specific statement
SELECT * FROM orders BEFORE (STATEMENT => '019c4be9-0000-...');

-- Clone a table to a previous state
CREATE TABLE orders_restored CLONE orders AT (VERSION => 42);
```

---

## 📌 Section 2: Pipeline Optimization & Broadcast Joins

---

### Q7. What steps would you take to optimize a data pipeline in Spark/Databricks?

**1. Data Layer Optimizations**
- Use **Delta Lake** with proper partitioning
- Run `OPTIMIZE` with **Z-ORDER** on high-cardinality filter columns
- Enable **Auto Optimize** and **Auto Compaction** in Databricks
- Use **Liquid Clustering** for dynamic partition pruning

**2. Join Optimizations**
- Use **Broadcast Joins** for small tables (< 10 MB default)
- Avoid **cross joins** and **shuffle-heavy joins** where possible
- Enable **AQE** to let Spark dynamically optimize shuffle partitions and joins

**3. Shuffle Optimizations**
- Tune `spark.sql.shuffle.partitions` (default 200 — often too high or too low)
- Use **AQE** to coalesce shuffle partitions dynamically
- Avoid unnecessary `distinct()`, `orderBy()` globally

**4. Serialization / UDF Optimizations**
- Replace **Python UDFs** with **Pandas UDFs** or **native Spark functions**
- Enable **Apache Arrow** for vectorized operations
- Avoid row-level Python processing

**5. Caching & Persistence**
- Cache intermediate DataFrames that are reused multiple times
- Use `DELTA CACHE` in Databricks for SSD-backed caching

**6. Cluster Sizing**
- Use **auto-scaling** clusters
- Right-size executors: balance memory vs. cores
- Enable **Photon Engine** in Databricks for vectorized CPU execution

**7. Monitoring**
- Use **Spark UI** to identify skewed stages, long tasks, spill
- Use **Databricks Query History** and **Ganglia metrics**

---

### Q8. What is Broadcast Join in Spark?

Broadcast Join is a join optimization where Spark **broadcasts (sends a copy of) the smaller table to all executor nodes**, avoiding a shuffle of the large table entirely.

Instead of reshuffling both datasets by join key, the small table is sent to every executor, and each executor performs a local hash lookup against its partition of the large table.

**Default threshold:** 10 MB (`spark.sql.autoBroadcastJoinThreshold = 10485760`)

```python
from pyspark.sql.functions import broadcast

result = large_df.join(broadcast(small_df), "user_id")
```

---

### Q9. How does Broadcast Join work internally?

1. **Driver collects** the small DataFrame (if within threshold)
2. **Driver serializes** it into a byte array
3. **Driver broadcasts** the byte array to all executors via the BlockManager
4. **Each executor deserializes** it into an in-memory hash map
5. **Each executor performs** a local hash join against its partition of the large table
6. **No shuffle** of the large table occurs — massive performance gain

**Internally uses:** `BroadcastHashJoin` physical plan node (visible in `explain()` output)

```python
# Verify broadcast join is being used
large_df.join(broadcast(small_df), "id").explain()
# Look for: BroadcastHashJoin in the physical plan
```

**Risk:** If the small table is not actually small, broadcasting causes **driver OOM** or **executor memory pressure**.

---

### Q10. How can we change or configure broadcast join behavior in Spark?

```python
# Change the threshold (bytes)
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", 50 * 1024 * 1024)  # 50 MB

# Disable broadcast joins entirely
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", -1)

# Force broadcast with hint
from pyspark.sql.functions import broadcast
df1.join(broadcast(df2), "key")

# SQL hint
spark.sql("SELECT /*+ BROADCAST(small_table) */ * FROM large_table JOIN small_table USING (id)")

# Control timeout for broadcast (seconds)
spark.conf.set("spark.sql.broadcastTimeout", 600)  # default 300s
```

**When AQE is enabled**, Spark can also dynamically choose broadcast joins at runtime even if statistics weren't available at planning time (`spark.sql.adaptive.autoBroadcastJoinThreshold`).

---

## 📌 Section 3: Adaptive Query Execution (AQE)

---

### Q11. What is AQE (Adaptive Query Execution) in Spark?

AQE is a **runtime query optimization framework** introduced in Spark 3.0. It re-optimizes query plans **after each shuffle stage completes**, using actual runtime statistics instead of relying solely on pre-execution estimates.

**Enabled by default in Spark 3.2+:**
```python
spark.conf.set("spark.sql.adaptive.enabled", True)
```

**Three core optimizations:**
1. **Dynamically coalescing shuffle partitions** — merges small post-shuffle partitions
2. **Dynamically switching join strategies** — converts SortMergeJoin to BroadcastHashJoin when a table turns out to be small
3. **Dynamically optimizing skew joins** — splits skewed partitions into smaller sub-tasks

---

### Q12. What are the different AQE parameters/configurations available in Spark?

```python
# Enable AQE
spark.conf.set("spark.sql.adaptive.enabled", True)

# Coalesce shuffle partitions
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", True)
spark.conf.set("spark.sql.adaptive.coalescePartitions.minPartitionNum", 1)
spark.conf.set("spark.sql.adaptive.advisoryPartitionSizeInBytes", "64MB")

# Skew join handling
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", True)
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionFactor", 5)      # partition > 5x median
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes", "256MB")

# Dynamic broadcast join conversion
spark.conf.set("spark.sql.adaptive.autoBroadcastJoinThreshold", "30MB")

# Local shuffle reader (avoids full fetch from shuffle)
spark.conf.set("spark.sql.adaptive.localShuffleReader.enabled", True)
```

---

### Q13. How does AQE improve Spark job performance?

| Problem | Without AQE | With AQE |
|---|---|---|
| **Too many small shuffle partitions** | 200 tiny tasks wasting overhead | Coalesces into fewer, right-sized partitions |
| **Data skew in joins** | One task processes 10x more data | Splits skewed partition into sub-tasks |
| **Over/under-estimated table size** | SortMergeJoin chosen for a small table | Converts to BroadcastHashJoin at runtime |
| **Stale statistics** | Wrong plan chosen based on old ANALYZE | Re-plans after each shuffle stage |

**Real-world impact:**
- Eliminates manual tuning of `spark.sql.shuffle.partitions`
- Reduces job time by 20–60% in skew-heavy workloads
- Reduces task failures from OOM in skewed joins

---

## 📌 Section 4: Z-Ordering & Bloom Filters

---

### Q14. You have a Delta table with 50 billion rows partitioned by event_date. Queries filter on user_id and event_date. Despite Z-Ordering on user_id, queries still scan multiple files. Why can Z-Ordering fail in this scenario?

**Root Causes:**

1. **Z-Ordering is scoped per partition**
   Z-Ordering co-locates rows within each `event_date` partition independently. If a single `user_id` appears across many `event_date` partitions, queries without a date filter must scan all partitions — Z-Order provides no cross-partition benefit.

2. **High cardinality of user_id**
   With 50B rows and potentially hundreds of millions of unique `user_id` values, the Z-Order clustering density per file is low. Min/max statistics overlap heavily across files, so data skipping fails.

3. **File size too small**
   If files are tiny (due to frequent small writes), even Z-Ordering results in too many files with overlapping ranges. Data skipping needs statistically representative files.

4. **Insufficient OPTIMIZE runs**
   Z-Ordering requires `OPTIMIZE` to compact and re-order. If OPTIMIZE hasn't been run recently (or incrementally), old files remain unordered.

5. **Z-Order on too many columns**
   Z-Ordering degrades with each additional column added. More columns = each column gets less clustering benefit.

6. **Event date not included in filter**
   If queries filter only on `user_id` (no `event_date`), partition pruning doesn't kick in and all partitions are scanned.

---

### Q15. How would you recover and optimize a Delta table when Z-Ordering is not effective?

**Strategy 1: Add Bloom Filters for user_id**
```sql
ALTER TABLE events SET TBLPROPERTIES (
  'delta.dataSkippingNumIndexedCols' = '32',
  'delta.bloomFilter.user_id.enabled' = 'true',
  'delta.bloomFilter.user_id.numItems' = '500000000',
  'delta.bloomFilter.user_id.fpp' = '0.01'
);
OPTIMIZE events ZORDER BY (user_id);
```

**Strategy 2: Liquid Clustering (Databricks Runtime 13.3+)**
```sql
-- No static partitions needed; clustering is dynamic
ALTER TABLE events CLUSTER BY (event_date, user_id);
OPTIMIZE events;
```

**Strategy 3: Re-partition by user_id hash bucket**
```python
# Create a bucket column for better locality
df = df.withColumn("user_bucket", (col("user_id").cast("long") % 1000))
df.write.partitionBy("event_date", "user_bucket").format("delta").save(...)
```

**Strategy 4: Increase file sizes before OPTIMIZE**
```sql
ALTER TABLE events SET TBLPROPERTIES ('delta.targetFileSize' = '134217728'); -- 128 MB
OPTIMIZE events ZORDER BY (user_id);
```

**Strategy 5: Regular incremental OPTIMIZE**
```python
# Only optimize newly added partitions (avoid full table scan)
spark.sql("OPTIMIZE events WHERE event_date >= '2024-01-01' ZORDER BY (user_id)")
```

---

### Q16. What is Bloom Filtering in Spark/Delta Lake?

A **Bloom Filter** is a **probabilistic data structure** that tests whether an element is definitely NOT in a set (no false negatives) or possibly in a set (with a configurable false positive rate).

In Delta Lake, Bloom Filters are stored as **per-file index metadata**. During query execution, before reading a file, Spark checks the Bloom Filter for the queried value. If the filter says "definitely not here", the file is skipped entirely.

**Properties:**
- Space-efficient (uses bit arrays)
- O(1) lookup time
- False positive rate (FPP) is configurable
- No false negatives — if filter says "not present", it's guaranteed

```sql
-- Enable Bloom Filter on a column
CREATE OR REPLACE TABLE users
USING DELTA
TBLPROPERTIES (
  'delta.bloomFilter.user_id.enabled' = 'true',
  'delta.bloomFilter.user_id.numItems' = '10000000',
  'delta.bloomFilter.user_id.fpp' = '0.01'    -- 1% false positive rate
) AS SELECT * FROM raw_users;
```

---

### Q17. What are real-world use cases of Bloom Filters in data engineering projects?

| Use Case | Description |
|---|---|
| **User lookup in event logs** | Filter files before scanning 50B event rows for specific `user_id` values |
| **Order ID search** | Quickly skip irrelevant files when querying by `order_id` |
| **Fraud detection** | Look up flagged `account_id` values across massive transaction tables |
| **CDC deduplication** | Check if a record ID already exists before inserting |
| **API log analysis** | Find specific `request_id` or `session_id` in petabyte-scale logs |
| **Clickstream analytics** | Point lookups on `device_id` or `cookie_id` columns |

**When Bloom Filters shine:**
- High-cardinality columns (user IDs, UUIDs, hashes)
- Point lookups (`WHERE user_id = '123'`)
- Columns with many distinct values that don't benefit from range-based Z-Order

---

### Q18. What is the difference between Bloom Filter and Z-Ordering?

| Dimension | Z-Ordering | Bloom Filter |
|---|---|---|
| **Mechanism** | Physically co-locates related rows in the same files | Probabilistic per-file membership index |
| **Query type** | Range queries, partial filters | Point lookups, equality filters |
| **Cardinality** | Works best with low-to-medium cardinality | Works best with high cardinality |
| **Storage cost** | No extra storage (reorders existing data) | Extra metadata stored per file |
| **Requires OPTIMIZE?** | Yes — must run OPTIMIZE ZORDER BY | No for reads; OPTIMIZE recommended for writes |
| **False positives** | N/A | Yes (configurable FPP) |
| **Multi-column** | Degrades with each extra column | Independent per column |

---

### Q19. When would you choose Bloom Filters over Z-Ordering?

**Choose Bloom Filters when:**
- Column has **very high cardinality** (user IDs, UUIDs, hashes, session IDs)
- Queries are **point lookups** (`WHERE id = 'X'`), not range scans
- Z-Order skipping is not effective due to data distribution
- You need **low-overhead per-file filtering** without physical rearrangement

**Choose Z-Ordering when:**
- Queries involve **range predicates** (`WHERE event_date BETWEEN ...`)
- Column cardinality is **moderate**
- You want **co-location** of related rows for multi-column filters
- The column is already a natural sort/cluster candidate

**Combine both** for compound queries:
```sql
-- Z-Order on date range + Bloom Filter on high-cardinality user_id
OPTIMIZE events ZORDER BY (event_date);
ALTER TABLE events SET TBLPROPERTIES (
  'delta.bloomFilter.user_id.enabled' = 'true',
  'delta.bloomFilter.user_id.numItems' = '100000000',
  'delta.bloomFilter.user_id.fpp' = '0.01'
);
```

---

## 📌 Section 5: PySpark UDF Optimization & Arrow

---

### Q20. A PySpark job using Python UDFs with Pandas and NumPy is taking 45+ minutes instead of 5–10 minutes. How would you optimize it?

**Diagnosis first:** Check Spark UI for:
- Long task durations (serialization overhead?)
- High GC time (memory pressure?)
- Skewed partition sizes?

**Optimization Steps:**

**Step 1: Replace Python UDFs with Pandas UDFs (Vectorized)**
```python
# BEFORE — Row-level Python UDF (slow)
from pyspark.sql.functions import udf
from pyspark.sql.types import DoubleType

@udf(DoubleType())
def normalize(val):
    return float(val) / 100.0

df = df.withColumn("normalized", normalize(col("amount")))

# AFTER — Pandas UDF (vectorized, Arrow-backed)
from pyspark.sql.functions import pandas_udf
import pandas as pd

@pandas_udf(DoubleType())
def normalize_vectorized(vals: pd.Series) -> pd.Series:
    return vals / 100.0

df = df.withColumn("normalized", normalize_vectorized(col("amount")))
```

**Step 2: Enable Apache Arrow**
```python
spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", True)
spark.conf.set("spark.sql.execution.arrow.maxRecordsPerBatch", 10000)
```

**Step 3: Replace UDFs with native Spark functions where possible**
```python
# Native functions are Catalyst-optimized and run in JVM
from pyspark.sql.functions import round, log, when
df = df.withColumn("normalized", col("amount") / 100.0)  # No UDF needed!
```

**Step 4: Check for data skew**
```python
# Repartition to balance data
df = df.repartition(200, "partition_key")
```

**Step 5: Avoid repeated Python process creation**
- Batch Pandas/NumPy operations inside a single Pandas UDF
- Avoid calling external processes inside UDFs

---

### Q21. How does Apache Arrow improve PySpark performance?

Apache Arrow is a **columnar, in-memory data format** that enables **zero-copy data interchange** between the JVM (Spark) and Python (Pandas/NumPy) processes.

**Without Arrow:**
1. Spark (JVM) serializes row data to Python using Pickle
2. Python deserializes row by row
3. Processes in Python
4. Re-serializes back row by row to JVM

**With Arrow:**
1. Spark keeps data in columnar Arrow format
2. Transfers entire column batches to Python as shared memory buffers
3. Pandas reads directly from Arrow buffers — **no deserialization**
4. Results returned as Arrow batches — no re-serialization overhead

**Performance gains:**
- 10–100x faster data transfer between JVM and Python
- Reduced GC pressure in both JVM and Python
- Required for **Pandas UDFs** and **toPandas()** optimizations

```python
# Enable Arrow optimization
spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", True)

# Arrow-backed toPandas()
pandas_df = spark_df.toPandas()  # Uses Arrow if enabled

# Arrow-backed createDataFrame from Pandas
spark_df = spark.createDataFrame(pandas_df)  # Uses Arrow if enabled
```

---

### Q22. What are the limitations of Python UDFs in Spark?

| Limitation | Detail |
|---|---|
| **No Catalyst optimization** | Python UDFs are black boxes; Catalyst cannot optimize inside them |
| **Serialization overhead** | Data must be serialized from JVM to Python and back for every row |
| **Row-by-row processing** | Each row crosses the JVM-Python boundary individually |
| **No predicate pushdown** | Filter conditions inside a UDF cannot be pushed to the data source |
| **Not null-safe by default** | Python UDFs receive `None` for null values; must handle explicitly |
| **High memory usage** | Python process runs separately; memory isn't shared with JVM heap |
| **Difficult to debug** | Stack traces are hard to interpret; errors in executors can be cryptic |
| **Not suitable for streaming** | Limited support in Structured Streaming contexts |

---

### Q23. When should we replace Python UDFs with Scala functions or Spark native functions?

**Replace with Native Spark Functions when:**
- The logic can be expressed with `pyspark.sql.functions` (string ops, math, conditionals, date functions)
- Performance is critical and the operation runs on millions+ rows
- You want Catalyst to optimize and push predicates

**Replace with Scala UDFs when:**
- You need JVM-native execution (no Python process overhead)
- The logic requires complex custom code not available natively
- You're operating in a latency-sensitive production pipeline
- You need to register reusable functions in the Hive metastore

**Keep Python UDFs (or upgrade to Pandas UDFs) when:**
- The logic uses Python-only libraries (NumPy, scikit-learn, custom ML models)
- Data science team owns and maintains the logic
- Batch size is small enough that overhead is acceptable

```scala
// Scala UDF — runs in JVM, no serialization overhead
import org.apache.spark.sql.functions.udf
val normalize = udf((v: Double) => v / 100.0)
df.withColumn("normalized", normalize(col("amount")))
```

---

### Q24. What is the difference between Python UDF, Pandas UDF, and Scala UDF in Spark?

| Feature | Python UDF | Pandas UDF | Scala UDF |
|---|---|---|---|
| **Execution** | Row-by-row in Python process | Vectorized batches via Arrow | Row-by-row in JVM |
| **Serialization** | Pickle (row-level) | Arrow columnar batches | None (native JVM) |
| **Performance** | Slowest | Fast (vectorized) | Fastest |
| **Catalyst optimization** | No | Partial | No (but in JVM) |
| **Null handling** | Manual | Pandas handles naturally | Manual |
| **Library support** | Full Python ecosystem | Full Python + Pandas | JVM libraries only |
| **Streaming support** | Limited | Yes (with `applyInPandas`) | Yes |
| **Use case** | Simple transformations | ML inference, vectorized math | High-perf custom logic |

```python
# Pandas UDF example
from pyspark.sql.functions import pandas_udf
import pandas as pd
import numpy as np

@pandas_udf("double")
def zscore(series: pd.Series) -> pd.Series:
    return (series - series.mean()) / series.std()

df.withColumn("z_amount", zscore(col("amount")))
```

---

### Q25. How do serialization and deserialization impact PySpark performance?

Spark is JVM-based. Python UDFs require **inter-process communication** between the JVM (executor) and a Python worker process:

1. **JVM serializes** each row using Pickle format
2. Data is **sent via socket** to the Python worker
3. Python worker **deserializes** each row
4. Python processes the row
5. Result is **serialized back** (Pickle)
6. **JVM deserializes** the result

**Performance impact:**
- Pickle serialization is slow and CPU-intensive
- Socket communication adds latency per row
- With 100M rows, this overhead becomes the dominant cost
- Memory doubles: data exists in both JVM and Python heap simultaneously

**Mitigation:**
- Use **Pandas UDFs** → Arrow replaces Pickle, batches replace rows
- Use **native Spark functions** → no Python process at all
- Use **Scala UDFs** → JVM-native, no inter-process overhead
- Tune `spark.sql.execution.arrow.maxRecordsPerBatch` (larger = fewer round trips)

---

### Q26. How can vectorized UDFs improve Spark execution time?

Vectorized UDFs (Pandas UDFs) process **entire column batches at once** using Apache Arrow, instead of row-by-row:

| Aspect | Standard Python UDF | Vectorized Pandas UDF |
|---|---|---|
| **Data transfer** | Row-by-row via Pickle | Columnar batch via Arrow |
| **Python invocations** | N (one per row) | N/batch_size |
| **NumPy/Pandas ops** | Not used | Fully vectorized |
| **Typical speedup** | 1x baseline | 10–100x over Python UDF |

```python
from pyspark.sql.functions import pandas_udf
import pandas as pd
import numpy as np

# Vectorized — entire column processed at once with NumPy
@pandas_udf("double")
def log_transform(s: pd.Series) -> pd.Series:
    return np.log1p(s)  # Vectorized NumPy operation on entire Series

df.withColumn("log_amount", log_transform(col("amount")))
```

**Key benefit:** NumPy and Pandas operations are implemented in C internally, making them orders of magnitude faster than Python loops.

---

### Q27. What are the best practices for optimizing Spark transformations involving NumPy/Pandas operations?

**1. Always use Pandas UDFs over Python UDFs for NumPy/Pandas logic**
```python
@pandas_udf("double")
def normalize(s: pd.Series) -> pd.Series:
    return (s - s.min()) / (s.max() - s.min())
```

**2. Enable Arrow and tune batch size**
```python
spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", True)
spark.conf.set("spark.sql.execution.arrow.maxRecordsPerBatch", 50000)
```

**3. Avoid calling `toPandas()` on large DataFrames**
- `toPandas()` collects all data to the driver — use only for small aggregated results

**4. Use `applyInPandas` for group-level Pandas operations**
```python
def normalize_group(key, pdf: pd.DataFrame) -> pd.DataFrame:
    pdf["normalized"] = (pdf["amount"] - pdf["amount"].mean()) / pdf["amount"].std()
    return pdf

df.groupBy("category").applyInPandas(normalize_group, schema=df.schema)
```

**5. Leverage native Spark SQL functions first**
```python
# Prefer native over UDF
from pyspark.sql.functions import log1p, stddev, mean
df.withColumn("log_amount", log1p(col("amount")))
```

**6. Avoid Python object creation in loops inside UDFs**
```python
# BAD — creates Python objects per row
@udf("double")
def bad_udf(x):
    result = SomeComplexClass(x)  # Object creation overhead
    return result.compute()

# GOOD — vectorized, no per-row object creation
@pandas_udf("double")
def good_udf(s: pd.Series) -> pd.Series:
    return s.apply(lambda x: x ** 2)  # Or better: s ** 2 (fully vectorized)
```

**7. Cache intermediate DataFrames used multiple times**
```python
preprocessed_df = df.withColumn(...).cache()
preprocessed_df.count()  # Materialize cache
```

**8. Use Spark's built-in ML for large-scale ML transformations**
- `pyspark.ml.feature.StandardScaler`, `VectorAssembler`, etc.
- These run in JVM with no Python overhead

---

## 📊 Quick Reference Summary

| Topic | Key Takeaway |
|---|---|
| Data Quality | DLT Expectations > Great Expectations > Custom PySpark validation |
| Delta Lake | ACID + Time Travel + Z-Order + Bloom Filters + MERGE |
| Time Travel | `VERSION AS OF` / `TIMESTAMP AS OF` — stored in `_delta_log` |
| Broadcast Join | Sends small table to all executors — threshold: 10 MB default |
| AQE | Runtime re-optimization: coalesce partitions, fix skew, upgrade joins |
| Z-Ordering | Range queries, moderate cardinality, co-location within partitions |
| Bloom Filter | Point lookups, high cardinality, probabilistic file skipping |
| Python UDF | Slowest — row-by-row Pickle serialization through Python process |
| Pandas UDF | Vectorized + Arrow — 10–100x faster than Python UDF |
| Scala UDF | JVM-native — fastest, no Python overhead |
| Arrow | Columnar in-memory format enabling zero-copy JVM ↔ Python transfer |

---

*Prepared from real interview questions — Databricks / Spark Senior Data Engineer round*
