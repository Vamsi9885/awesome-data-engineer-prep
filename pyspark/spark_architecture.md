# 🧠 Spark Architecture Deep Dive (PySpark Interview Core)

This is the most important Spark file for advanced interviews.  
If you can explain this clearly, you can handle most Amazon/Uber/Netflix PySpark rounds.

---

## 1) Concept Explanation (Interview-Focused)

Spark is a **distributed compute engine** optimized for large-scale data processing through:
- In-memory computation
- DAG-based execution planning
- Optimized query engine (Catalyst + Tungsten)
- Fault-tolerant lineage model

At a high level:

```text
Your PySpark Code
   ↓
Driver builds Logical Plan
   ↓
Catalyst Optimizer creates Physical Plan
   ↓
DAG Scheduler splits Job -> Stages
   ↓
Task Scheduler launches Tasks on Executors
   ↓
Executors compute partitions + shuffle data
   ↓
Results written to sink / returned to driver
```

---

## 2) Core Components

## Driver
- Runs your Spark application main process.
- Creates SparkSession / SparkContext.
- Builds logical and physical plans.
- Coordinates scheduling and metadata.
- Holds task and stage-level orchestration (not actual heavy data processing).

**Interview trap:** Driver is not “doing all work”; executors do data-heavy work.

## Executors
- JVM processes on worker nodes.
- Execute tasks on partitions.
- Keep cached blocks in memory.
- Perform shuffle read/write.
- Report metrics/status back to driver.

## Cluster Manager
Allocates resources for driver/executors. Common choices:
- **YARN** (Hadoop ecosystem)
- **Kubernetes** (cloud-native)
- **Standalone** (Spark’s own manager)

## Worker Nodes
Machines that host executor processes and local disk used for spill/shuffle files.

---

## 3) Execution Flow: Job → Stage → Task

When you run an **action** (`count`, `show`, `write`, `collect`), Spark triggers execution.

### Units of work

- **Job**: created per action.
- **Stage**: group of tasks between shuffle boundaries.
- **Task**: smallest unit; one task per partition.

```text
Action: df.groupBy("city").count().write.parquet(...)
                └── Job 1
                    ├── Stage 1 (read + filter) [narrow ops]
                    ├── Stage 2 (shuffle + aggregate) [wide op boundary]
                    └── Stage 3 (write output)
```

### DAG and Lazy Evaluation

Transformations are lazy; Spark builds a DAG first, then executes at action time.

```text
read -> filter -> withColumn -> groupBy -> agg -> write
 ^----------------------------------------------------^
       planned lazily as lineage graph until action
```

---

## 4) Spark Internals (Basic → Moderate)

## 4.1 Catalyst Optimizer

Catalyst is Spark SQL/DataFrame query optimizer with phases:

1. **Analysis**: Resolve table/column references and types.
2. **Logical optimization**:
   - Constant folding
   - Predicate pushdown
   - Column pruning
3. **Physical planning**: Select operators (e.g., SortMergeJoin, BroadcastHashJoin)
4. **Code generation**: Whole-stage codegen where possible.

You can inspect plans with:

```python
df.explain("extended")
```

## 4.2 Tungsten Engine

Tungsten improves CPU/memory efficiency via:
- Binary memory layout (`UnsafeRow`)
- Off-heap memory management
- Cache-friendly execution
- Whole-stage code generation

Practical impact:
- Less GC pressure
- Better CPU utilization
- Faster joins/aggregations

## 4.3 DAG Scheduler vs Task Scheduler

- **DAG Scheduler**:
  - Converts logical execution graph into stages.
  - Determines shuffle boundaries.
  - Handles stage retries on failures.

- **Task Scheduler**:
  - Launches tasks on available executors.
  - Applies locality preferences.
  - Handles speculative execution and failed task retries.

---

## 5) Memory Management (Execution vs Storage)

Spark unified memory has two major logical uses:

- **Execution Memory**:
  - Shuffles
  - Sorts
  - Joins
  - Aggregations

- **Storage Memory**:
  - Cached/persisted DataFrames/RDDs
  - Broadcast variables

If memory is insufficient:
- Execution may spill to disk (slow)
- Cached blocks may be evicted
- Excessive spill indicates partition sizing/config issues

```text
Executor Memory
 ├── Execution region (compute heavy)
 └── Storage region (cache/broadcast)
      ↔ dynamic borrowing depending on pressure
```

---

## 6) Data Flow: Narrow vs Wide + Shuffle (Critical)

## Narrow Transformations
No cross-partition movement required.
Examples:
- `map`, `filter`, `select`, `withColumn`

Each output partition depends on one input partition.

## Wide Transformations
Require data movement (shuffle) across partitions.
Examples:
- `groupBy`, `join` (non-broadcast), `distinct`, `repartition`

### Shuffle Internals (why expensive)
Shuffle includes:
1. Map-side partitioning and spill files
2. Disk IO and network transfer
3. Reduce-side fetch + merge + sort
4. Possible skew amplification and stragglers

**Cost drivers**:
- Network IO
- Disk spill
- Serialization/deserialization
- Data skew (one reducer gets huge partition)

---

## 7) PySpark Code Example: Architecture-Aware ETL

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as _sum, broadcast

spark = (
    SparkSession.builder
    .appName("architecture-aware-etl")
    .config("spark.sql.adaptive.enabled", "true")
    .config("spark.sql.shuffle.partitions", "300")
    .getOrCreate()
)

# Read (logical plan only)
orders = spark.read.parquet("s3://lake/orders/")
customers = spark.read.parquet("s3://lake/dim/customers/")

# Narrow transformations
orders_f = (
    orders
    .filter(col("order_status") == "COMPLETE")
    .filter(col("order_date") >= "2024-01-01")
    .select("order_id", "customer_id", "order_date", "amount")
)

# Join strategy choice: broadcast small dimension to avoid shuffle join
enriched = orders_f.join(broadcast(customers.select("customer_id", "segment")), "customer_id", "left")

# Wide transformation (shuffle boundary)
agg = enriched.groupBy("segment").agg(_sum("amount").alias("gmv"))

# Action triggers Job -> Stage -> Task execution
agg.write.mode("overwrite").parquet("s3://lake/marts/segment_gmv/")
```

---

## 8) DAG Explanation for Above Code

```text
Stage 1:
  Read orders -> filter -> select      (narrow)

Stage 2:
  Read customers (small) -> broadcast  (no large shuffle)

Stage 3:
  Hash aggregate by segment            (shuffle for groupBy)

Stage 4:
  Write parquet output                 (final stage)
```

Check in Spark UI:
- SQL tab for query plan and operator metrics
- Stages tab for skew/stragglers
- Executors tab for memory + GC + spill

---

## 9) Real-World Scenario: Databricks Job Execution

**Scenario:** Daily e-commerce ETL in Databricks on S3 + Delta

Pipeline:
1. Bronze ingestion (raw JSON to Delta)
2. Silver cleaning + dedupe
3. Gold business aggregates for BI

How job runs internally:
- Notebook/Job cluster launches driver + executors.
- Auto-scaling handles peak loads.
- AQE adapts join strategies at runtime.
- Delta stats + data skipping reduce scanned files.
- Failed tasks retry automatically; checkpointed writes give consistency.

Operational checks:
- Stage with highest shuffle read/write
- Skewed tasks (task duration outliers)
- Spill to disk and executor lost events
- File count explosion in output path

---

## 10) Common Mistakes

1. Thinking “more executors always faster” (can increase shuffle overhead and cost).
2. Ignoring partition sizing (too small = scheduler overhead, too large = OOM/spill).
3. Using `collect()` in production flows.
4. Caching huge DataFrames without reuse count.
5. Not reading Spark UI; tuning blindly.
6. Forgetting broadcast threshold tuning for small dimensions.
7. Not handling skew in wide transformations.

---

## 11) Performance Tips (Architecture-Aware)

- Push filters early (predicate pushdown).
- Select only needed columns (column pruning).
- Prefer broadcast joins for small dimensions.
- Avoid unnecessary `repartition`; use only when required.
- Tune shuffle partitions based on data size.
- Enable AQE:
  - `spark.sql.adaptive.enabled=true`
- Watch spill and skew in Spark UI; optimize iteratively.
- Prefer built-in functions over Python UDFs.

---

## 12) 🔥 Interview Questions (Basic → Advanced → Product)

## Basic
1. Explain Spark architecture in detail.
2. What happens when you run an action in Spark?
3. What is DAG in Spark?
4. Difference between Job, Stage, and Task?
5. What is shuffle and why is it expensive?

## Advanced
1. Explain Catalyst optimizer stages with example.
2. DAG Scheduler vs Task Scheduler: who does what?
3. Why can two actions on same DataFrame trigger two jobs?
4. How does Spark handle executor failure and task retry?
5. Explain execution vs storage memory and spill behavior.

## Product/Scenario-Based
1. A Databricks job is slow only during `groupBy`; how do you diagnose and fix?
2. Your join stage has 1 task running 10x longer than others. Root cause and remediation?
3. How would you optimize 5 TB daily ETL where small dimension joins dominate?
4. Why did pipeline cost increase after scaling cluster size?

## Follow-up Drill Questions
- What metric in Spark UI confirms skew?
- When does AQE change join strategy at runtime?
- Why might broadcast join still fail?
- How do you choose `spark.sql.shuffle.partitions`?
- How do you explain Spark being faster than Hadoop MapReduce in one minute?

---

## 13) One-Minute Interview Summary

Spark is fast because it builds an optimized DAG, uses Catalyst for plan optimization, Tungsten for CPU/memory-efficient execution, and runs tasks in parallel on executors. Actions trigger jobs, jobs split into stages at shuffle boundaries, and tasks process partitions. Wide transformations introduce shuffle, which is expensive due to network and disk IO. Performance tuning is mostly about reducing shuffle, handling skew, choosing correct join strategy, tuning partitions, and validating everything in Spark UI.
