# PySpark Interview Questions (Real-World, Product-Focused)

## Interviewer Lens (What Gets You Hired)
- Can you explain Spark internals, not just syntax?
- Can you debug and optimize production jobs?
- Can you reason about trade-offs (latency vs cost vs correctness)?
- Can you tie technical decisions to business outcomes?

## Common Mistakes
- Saying “Spark is fast” without explaining Catalyst/Tungsten/columnar execution.
- Using `repartition(200)` blindly.
- Caching everything.
- Ignoring skew and shuffle metrics in Spark UI.
- No mention of partition pruning or broadcast joins.

## Pro Tips
- Always explain execution flow: read → transform DAG → shuffle boundaries → write.
- Mention data volume and cardinality assumptions.
- Talk through observability (Spark UI, executor metrics, stage failures).
- Prefer narrow transformations when possible.

---

## 1) Spark Architecture Overview

### Question
Explain Spark architecture to a new engineer.

### Why Interviewers Ask This
Tests foundation required for performance tuning.

### Approach / Thought Process
1. Describe driver, executors, cluster manager.
2. Explain jobs, stages, tasks mapping.
3. Connect architecture to fault tolerance.

### Answer (Detailed)
Spark has:
- **Driver**: plans DAG, schedules tasks, coordinates job.
- **Executors**: run tasks, store cached data.
- **Cluster Manager**: YARN/K8s/Standalone allocates resources.
- **Jobs/Stages/Tasks**: Action triggers job; shuffle splits stages; tasks run per partition.

Fault tolerance is via lineage: lost partition is recomputed from source transformations.

### Follow-Up Questions
- Difference between client and cluster deploy mode?
- How does dynamic allocation work?
- What happens if driver dies?

---

## 2) Transformations vs Actions

### Question
What is the difference between transformations and actions?

### Why Interviewers Ask This
Core lazy evaluation concept.

### Approach / Thought Process
1. Define each.
2. Show examples.
3. Explain when computation actually starts.

### Answer (Detailed)
- **Transformations** (`select`, `filter`, `join`) build logical plan lazily.
- **Actions** (`count`, `collect`, `write`, `show`) trigger execution.
Spark optimizes the entire transformation chain before running action.

```python
df2 = df.filter("status = 'completed'").groupBy("city").count()  # lazy
df2.show()  # action triggers execution
```

### Follow-Up Questions
- Is `cache()` an action?
- Why is laziness useful?
- What if two actions are called on same DataFrame?

---

## 3) DAG Execution

### Question
How does Spark execute a DAG when action is triggered?

### Why Interviewers Ask This
Measures internal understanding for optimization.

### Approach / Thought Process
1. Logical plan generation.
2. Catalyst optimization.
3. Physical plan and stage generation.
4. Task scheduling and execution.

### Answer (Detailed)
Action triggers:
1. Build unresolved logical plan.
2. Catalyst applies rule-based + cost-based optimizations.
3. Physical plan selected (join strategy, scans).
4. DAG split into stages at shuffle boundaries.
5. Tasks submitted per partition.
6. Results materialized to sink/driver.

### Follow-Up Questions
- How to inspect plan (`explain`)?
- AQE impact on physical plan?
- Where does whole-stage codegen fit?

---

## 4) Why Spark Is Fast?

### Question
Why is Spark generally faster than classic MapReduce?

### Why Interviewers Ask This
Tests whether candidate understands execution engine internals.

### Approach / Thought Process
1. In-memory processing.
2. DAG optimization.
3. Tungsten/whole-stage codegen.
4. Better API and execution model.

### Answer (Detailed)
Spark is faster because:
- Caches intermediate data in memory.
- Avoids writing to disk between each step (unlike MR).
- Optimizes query plan using Catalyst.
- Uses Tungsten for efficient memory management.
- Whole-stage code generation compiles operations into JVM bytecode.
- Supports vectorized/columnar execution with Parquet/ORC.

### Follow-Up Questions
- Cases where Spark can still be slow?
- When does spilling happen?
- How does serialization affect speed?

---

## 5) What Happens When an Action Is Triggered?

### Question
Describe internals when `.count()` is called.

### Why Interviewers Ask This
Checks precise lifecycle understanding.

### Approach / Thought Process
1. Plan creation.
2. Optimization.
3. Stage/task execution.
4. Result aggregation.

### Answer (Detailed)
On `.count()`:
1. Spark finalizes logical plan.
2. Optimizes filters/projections/join strategies.
3. Creates physical plan.
4. Splits into stages by shuffles.
5. Schedules tasks to executors.
6. Executors process partitions and return partial counts.
7. Driver aggregates and returns final count.

### Follow-Up Questions
- Why can `.count()` be expensive?
- Alternative for quick sanity check?
- Difference between `.count()` and `.isEmpty()` behavior?

---

## 6) Shuffle Deep Dive

### Question
Explain shuffle and why it is expensive.

### Why Interviewers Ask This
Critical for large-scale Spark performance tuning.

### Approach / Thought Process
1. Define shuffle.
2. Explain disk/network/sort costs.
3. Mention skew and spill.
4. Explain mitigation.

### Answer (Detailed)
Shuffle redistributes data across partitions for operations like `groupBy`, `join`, `distinct`.
Costs:
- Serialization/deserialization
- Network transfer
- Disk I/O spill
- Sort/merge overhead
- Straggler tasks from skew

Mitigation:
- Reduce data early (`filter/select`)
- Use broadcast joins
- Tune shuffle partitions
- Handle skew with salting/repartitioning
- Enable AQE

### Follow-Up Questions
- How to detect shuffle bottleneck in Spark UI?
- Difference between sort-based and hash-based aggregation?
- How does AQE reduce shuffle impact?

---

## 7) cache vs persist

### Question
Difference between `cache()` and `persist()` and when to use each?

### Why Interviewers Ask This
Tests memory strategy and cost awareness.

### Approach / Thought Process
1. Define default storage level.
2. Explain alternatives.
3. Use practical scenarios.

### Answer (Detailed)
`cache()` == `persist(StorageLevel.MEMORY_AND_DISK)` (for DataFrame API in Spark SQL context; behavior historically differs for RDD).
`persist()` lets you choose storage level (e.g., MEMORY_ONLY, DISK_ONLY, MEMORY_AND_DISK_SER).

Use cache/persist only when:
- Data reused multiple times.
- Recompute cost high.
- Storage fits reasonably.

```python
from pyspark import StorageLevel
df.persist(StorageLevel.MEMORY_AND_DISK)
```

### Follow-Up Questions
- Why cache can slow jobs?
- When to `unpersist()`?
- MEMORY_ONLY vs MEMORY_AND_DISK tradeoff?

---

## 8) repartition vs coalesce

### Question
When do you use repartition vs coalesce?

### Why Interviewers Ask This
Partition management is core to performance and output layout.

### Approach / Thought Process
1. Explain shuffle behavior.
2. Explain increasing/decreasing partitions.
3. Use write-path examples.

### Answer (Detailed)
- `repartition(n)` does full shuffle; can increase or decrease partitions; balanced output.
- `coalesce(n)` usually avoids full shuffle; mostly used to reduce partitions cheaply.

```python
df_large = df.repartition(400, "country")
df_small = df_large.coalesce(100)
```
Use repartition before heavy joins/groupBy; coalesce before final write small file count.

### Follow-Up Questions
- Why `coalesce(1)` is risky?
- How to pick partition count?
- Interaction with `spark.sql.shuffle.partitions`?

---

## 9) Debug a Slow Spark Job (Scenario)

### Question
A job that used to run in 20 min now takes 2 hours. How do you debug?

### Why Interviewers Ask This
Assesses production troubleshooting method.

### Approach / Thought Process
1. Validate data volume/schema changes.
2. Inspect Spark UI (stages, skew, spill, GC, failed tasks).
3. Check plan changes and joins.
4. Apply targeted fixes.

### Answer (Detailed)
Debug flow:
1. Compare input size and partition counts.
2. Inspect Spark UI:
   - Which stage dominates runtime?
   - Task time variance (skew)?
   - Shuffle read/write and spill?
3. Run `df.explain("formatted")` for unexpected sort-merge join, missing pushdown, etc.
4. Check small files explosion.
5. Fix:
   - Filter/project earlier
   - Broadcast dimension table
   - Adjust partitions
   - Handle skew
   - Tune executor memory/cores

### Follow-Up Questions
- Which Spark UI tabs matter most?
- How to prove optimization worked?
- What alerts would you add for early detection?

---

## 10) Handle Data Skew (Scenario)

### Question
One key has 40% of data causing stragglers. What do you do?

### Why Interviewers Ask This
Skew handling separates senior vs basic Spark engineers.

### Approach / Thought Process
1. Identify skewed keys.
2. Pick mitigation approach.
3. Validate correctness/performance.

### Answer (Detailed)
Options:
- **Salting** skewed keys for parallelism.
- **Broadcast join** if opposite side small.
- **AQE skew join** (`spark.sql.adaptive.skewJoin.enabled=true`).
- Split hot keys and process separately.

```python
from pyspark.sql import functions as F
salted = fact.withColumn("salt", (F.rand()*10).cast("int"))
dim_expanded = dim.crossJoin(spark.range(10).toDF("salt"))
joined = salted.join(dim_expanded, ["key","salt"])
```

### Follow-Up Questions
- Risks of salting?
- How to choose salt buckets?
- Can skew happen in aggregations too?

---

## 11) Optimize Joins (Scenario)

### Question
How do you optimize joins in PySpark on large datasets?

### Why Interviewers Ask This
Join tuning is high-impact in distributed systems.

### Approach / Thought Process
1. Profile table sizes/cardinality.
2. Choose join strategy.
3. Reduce data before join.

### Answer (Detailed)
- Select only needed columns before join.
- Filter early.
- Broadcast small dimension tables.
- Repartition by join key for large-large joins.
- Avoid UDF-based join keys.
- Enable AQE.

```python
from pyspark.sql.functions import broadcast
result = fact.join(broadcast(dim), "product_id", "left")
```

### Follow-Up Questions
- Broadcast threshold configs?
- Sort-merge vs shuffle-hash join?
- How to handle skewed joins?

---

## 12) Explain Physical Plan

### Question
How do you read `explain("formatted")` and use it?

### Why Interviewers Ask This
Tests practical optimization workflow.

### Approach / Thought Process
1. Spot scans, filters, projection pushdown.
2. Identify join strategy.
3. Find exchange/shuffle nodes.

### Answer (Detailed)
Use `explain("formatted")` to inspect:
- Data source scans and predicate pushdown.
- Number of `Exchange` operators (shuffle boundaries).
- Join type (BroadcastHashJoin vs SortMergeJoin).
- AQE coalesced partitions.
Then tune based on observed bottleneck.

### Follow-Up Questions
- Difference logical vs physical plan?
- Why plan may differ at runtime with AQE?
- How to persist plan snapshots in CI checks?

---

## 13) Small Files Problem

### Question
Why are small files harmful in Spark and how to fix?

### Why Interviewers Ask This
Operational scaling issue in lakehouse pipelines.

### Approach / Thought Process
1. Explain metadata/listing overhead.
2. Explain task scheduling overhead.
3. Provide compaction strategies.

### Answer (Detailed)
Small files cause:
- High metadata overhead (listing/opening).
- Too many tiny tasks.
- Inefficient scan throughput.

Fix:
- Control partitioning before write.
- Batch/compact output files.
- Use optimize/compaction jobs (e.g., Delta OPTIMIZE).
- Tune `maxRecordsPerFile`.

### Follow-Up Questions
- How many files per partition is healthy?
- Compaction cadence strategy?
- Impact on downstream BI queries?

---

## 14) Partition Pruning

### Question
What is partition pruning and why important?

### Why Interviewers Ask This
Tests data layout and query-performance fundamentals.

### Approach / Thought Process
1. Explain partitioned table layout.
2. Show filter on partition column.
3. Connect to I/O reduction.

### Answer (Detailed)
If dataset partitioned by `dt`, query with `where dt='2026-01-01'` reads only relevant partition files.
Without pruning, Spark scans all partitions, increasing cost and latency.

```python
df = spark.read.parquet("s3://bucket/orders/")
df.filter("dt = '2026-01-01'").count()
```

### Follow-Up Questions
- Partitioning by high-cardinality columns?
- Partition vs bucketing?
- How does dynamic partition pruning work?

---

## 15) UDF vs Built-in Functions

### Question
Why avoid Python UDF when possible?

### Why Interviewers Ask This
Performance and engine optimization awareness.

### Approach / Thought Process
1. Explain serialization/Python boundary cost.
2. Explain Catalyst optimization loss.
3. Suggest alternatives.

### Answer (Detailed)
Python UDFs:
- Force data serialization JVM↔Python.
- Prevent many Catalyst optimizations.
- Usually slower than SQL built-ins or pandas UDF (in some contexts).

Prefer:
- Spark SQL built-in expressions
- `expr()`, `when`, `regexp_extract`
- Pandas UDF only when necessary and measured.

### Follow-Up Questions
- Arrow’s role in pandas UDF?
- Scalar vs grouped map UDF?
- How to benchmark UDF cost?

---

## 16) Broadcast Join Threshold

### Question
How does Spark decide to broadcast, and how can you control it?

### Why Interviewers Ask This
Join optimization tuning depth.

### Approach / Thought Process
1. Explain auto threshold.
2. Manual broadcast hint.
3. Risk of large broadcast.

### Answer (Detailed)
Spark can auto-broadcast small table under threshold (`spark.sql.autoBroadcastJoinThreshold`).
You can force using hint:

```python
fact.join(broadcast(dim), "id")
```

Too-large broadcast can OOM executors; always validate table size after filters.

### Follow-Up Questions
- Why broadcast disabled sometimes?
- AQE can change join strategy at runtime?
- Broadcast timeout configs?

---

## 17) AQE (Adaptive Query Execution)

### Question
What is AQE and why useful?

### Why Interviewers Ask This
Modern Spark optimization feature knowledge.

### Approach / Thought Process
1. Runtime optimization definition.
2. Key AQE features.
3. Practical impact.

### Answer (Detailed)
AQE adapts plan at runtime using observed stats:
- Coalesces shuffle partitions.
- Converts sort-merge join to broadcast join when possible.
- Handles skewed partitions.
This improves performance and resource usage on unpredictable data distributions.

### Follow-Up Questions
- When can AQE hurt?
- Required configs?
- How to validate AQE effects in UI/plan?

---

## 18) Structured Streaming Basics

### Question
Explain micro-batch model in Structured Streaming.

### Why Interviewers Ask This
Streaming is common in Uber/Netflix-like systems.

### Approach / Thought Process
1. Input source to incremental query.
2. Trigger interval and state.
3. Output sink and checkpointing.

### Answer (Detailed)
Structured Streaming treats stream as unbounded table:
- Reads source (Kafka, files).
- Runs incremental execution in micro-batches.
- Maintains state for aggregations/joins.
- Writes to sink with checkpointing for recovery.

### Follow-Up Questions
- Exactly-once guarantees?
- Watermarking role?
- Continuous processing mode vs micro-batch?

---

## 19) Watermarking in Streaming

### Question
Why watermarking is needed in event-time aggregations?

### Why Interviewers Ask This
Late data handling and state management.

### Approach / Thought Process
1. Define late data.
2. Explain state retention problem.
3. Show watermark behavior.

### Answer (Detailed)
Without watermark, state grows indefinitely.
Watermark defines allowed lateness (e.g., 10 minutes), so Spark can evict old state and finalize windows while still accepting moderately late events.

```python
stream_df.withWatermark("event_ts", "10 minutes") \
         .groupBy(window("event_ts","5 minutes"), "user_id").count()
```

### Follow-Up Questions
- What happens to too-late data?
- Watermark vs trigger interval?
- Multiple stream join watermark handling?

---

## 20) Checkpointing

### Question
What does checkpointing do in Spark streaming?

### Why Interviewers Ask This
Reliability and fault tolerance in production pipelines.

### Approach / Thought Process
1. Explain state + offsets persistence.
2. Recovery semantics.
3. Correct checkpoint hygiene.

### Answer (Detailed)
Checkpoint stores:
- Processed offsets
- Stateful operator state
- Metadata for query progress

On failure, job resumes from checkpoint instead of restarting from scratch, enabling near exactly-once behavior with compatible sinks.

### Follow-Up Questions
- Can you reuse same checkpoint for modified query?
- Checkpoint corruption recovery?
- Checkpoint location best practices?

---

## 21) Exactly-Once vs At-Least-Once

### Question
How do you achieve exactly-once semantics in Spark pipelines?

### Why Interviewers Ask This
Data correctness under failure is critical.

### Approach / Thought Process
1. Clarify end-to-end vs component-level guarantees.
2. Combine idempotent sink + transactional writes + checkpoint.
3. Mention practical constraints.

### Answer (Detailed)
True exactly-once is end-to-end property:
- Source with replayable offsets (Kafka)
- Spark checkpoint for progress
- Idempotent or transactional sink (Delta merge/upsert)
- Dedup keys for reprocessing safety

### Follow-Up Questions
- Why file sinks may produce duplicates?
- How do upserts help?
- How to test failure/restart correctness?

---

## 22) Incremental ETL Design in Spark

### Question
How would you design daily incremental ETL?

### Why Interviewers Ask This
Tests practical batch pipeline design.

### Approach / Thought Process
1. Change detection by watermark/high-watermark.
2. Transform and dedup.
3. Merge into target.

### Answer (Detailed)
Pattern:
1. Read source where `updated_at > last_success_ts`.
2. Dedup latest per business key.
3. Apply transformations.
4. Upsert into target table.
5. Store run metadata for idempotency.

### Follow-Up Questions
- How to handle late updates?
- Backfill strategy?
- Schema evolution handling?

---

## 23) SCD Type 2 in PySpark

### Question
How to implement SCD2 dimension in Spark?

### Why Interviewers Ask This
Common DE interview and production requirement.

### Approach / Thought Process
1. Define business key/current flag/effective dates.
2. Detect changes using hash of tracked columns.
3. Expire old row and insert new row.

### Answer (Detailed)
Use merge logic:
- Match on business key and current_flag=1.
- If changed: set old row `effective_to = new_effective_from - 1`, `current_flag=0`.
- Insert new current row.

Delta Lake `MERGE INTO` simplifies SCD2 and atomicity.

### Follow-Up Questions
- Handling out-of-order updates?
- Surrogate key generation?
- Performance of large merge operations?

---

## 24) Executor Memory Tuning

### Question
How do you tune executor memory for a heavy shuffle job?

### Why Interviewers Ask This
Resource tuning competency.

### Approach / Thought Process
1. Observe OOM/spill/GC.
2. Adjust executor memory/cores/instances balance.
3. Avoid oversized executors.

### Answer (Detailed)
Guidelines:
- Check spill and GC time in Spark UI.
- Increase executor memory if frequent spills.
- Reduce cores per executor if GC high.
- Use more moderate executors vs few huge ones.
- Tune shuffle partitions and serialization (Kryo if relevant).

### Follow-Up Questions
- Why too many cores per executor can hurt?
- Executor memory overhead role?
- Dynamic allocation interactions?

---

## 25) Data Skipping and Z-Ordering (Lakehouse)

### Question
How do Delta optimizations like Z-ORDER help Spark queries?

### Why Interviewers Ask This
Modern lakehouse operational tuning.

### Approach / Thought Process
1. Explain file-level stats and pruning.
2. Explain clustering locality.
3. Discuss trade-off with write cost.

### Answer (Detailed)
- File stats (min/max) allow skipping irrelevant files.
- Z-ORDER co-locates frequently filtered columns.
- Improves selective query latency significantly.
Trade-off: extra compute during optimize/maintenance.

### Follow-Up Questions
- When not to Z-ORDER?
- Difference from partitioning?
- Optimize cadence design?

---

## 26) PySpark Join Skew + AQE Scenario

### Question
You enabled AQE but still see stragglers in join stage. What next?

### Why Interviewers Ask This
Advanced troubleshooting under partial optimization.

### Approach / Thought Process
1. Verify skew join config active.
2. Inspect key distribution.
3. Apply manual skew strategy.

### Answer (Detailed)
If AQE insufficient:
- Identify hot keys from profiling.
- Split hot and non-hot keys.
- Process hot keys separately with salting/broadcast.
- Recombine outputs.
Also verify skew configs and Spark version behavior.

### Follow-Up Questions
- How to automate skew-key detection?
- Cost impact of split strategy?
- Correctness validation approach?

---

## 27) Driver OOM with collect()

### Question
Why does `collect()` crash driver and what alternatives exist?

### Why Interviewers Ask This
Basic distributed computing safety.

### Approach / Thought Process
1. Explain data movement to driver.
2. Propose bounded alternatives.

### Answer (Detailed)
`collect()` pulls entire dataset to driver memory.
Alternatives:
- `show()`, `take(n)`, `limit(n).toPandas()` (small n)
- Write to storage and inspect sample
- Aggregations in cluster instead of pulling raw rows

### Follow-Up Questions
- Is `toPandas()` safer?
- How to debug without collect?
- When collect is acceptable?

---

## 28) Handling Corrupt Records

### Question
How do you handle corrupt JSON/CSV rows in Spark ingestion?

### Why Interviewers Ask This
Data quality robustness in production.

### Approach / Thought Process
1. Use permissive mode and corrupt column capture.
2. Route bad records to quarantine.
3. Monitor data quality metrics.

### Answer (Detailed)
Read with schema and corrupt capture:
```python
df = spark.read.option("mode","PERMISSIVE") \
    .option("columnNameOfCorruptRecord","_corrupt_record") \
    .json(path)
good = df.filter("_corrupt_record IS NULL")
bad = df.filter("_corrupt_record IS NOT NULL")
```
Write `bad` to quarantine for triage and alerting.

### Follow-Up Questions
- Fail-fast vs permissive mode trade-off?
- How to avoid schema drift surprises?
- Governance on bad-record SLAs?

---

## 29) Explain Narrow vs Wide Transformations

### Question
What are narrow and wide transformations? Give examples.

### Why Interviewers Ask This
Helps reason about shuffles and stage boundaries.

### Approach / Thought Process
1. Define dependency type.
2. Map to shuffle behavior.
3. Show examples.

### Answer (Detailed)
- **Narrow**: Each output partition depends on one input partition (e.g., `map`, `filter`); no shuffle.
- **Wide**: Output partition depends on many input partitions (e.g., `groupBy`, `join`); requires shuffle.

Wide transformations usually dominate runtime due to network and sort.

### Follow-Up Questions
- Can repartition convert narrow chain to wide?
- How do wide transforms create stages?
- Is sort always wide?

---

## 30) Broadcast Variable vs Broadcast Join

### Question
Difference between Spark broadcast variable and broadcast join hint?

### Why Interviewers Ask This
Clarifies API-level vs SQL optimizer-level concepts.

### Approach / Thought Process
1. Define each.
2. Explain use cases.

### Answer (Detailed)
- Broadcast variable: distribute read-only object to executors in RDD/DataFrame custom logic.
- Broadcast join: optimizer strategy for joining small table to large table without shuffle on large side.

They solve different problems but both reduce network overhead.

### Follow-Up Questions
- Memory implications?
- When broadcast variable becomes anti-pattern?
- How to monitor broadcast size?

---

## 31) Spark Serialization

### Question
How does serialization affect Spark performance?

### Why Interviewers Ask This
Deep performance tuning topic.

### Approach / Thought Process
1. Explain object transfer/storage cost.
2. Mention serializer choices.
3. Relate to shuffle and cache.

### Answer (Detailed)
Serialization affects:
- Shuffle transfer size
- Cache memory footprint
- CPU for encode/decode
Kryo serializer is often faster and more compact than Java serializer for many workloads.

### Follow-Up Questions
- How to enable Kryo?
- Can serialization hurt CPU too much?
- Any compatibility concerns?

---

## 32) Skipping Unnecessary Columns

### Question
Why does selecting required columns early matter?

### Why Interviewers Ask This
Practical optimization habit.

### Approach / Thought Process
1. Reduce I/O and memory.
2. Improve shuffle payload.
3. Enable better pushdown.

### Answer (Detailed)
Project only required columns ASAP:
- Less scan data from source.
- Smaller serialized rows across network.
- Better cache usage and lower GC.

```python
df = spark.read.parquet(path).select("order_id","customer_id","amount","dt")
```

### Follow-Up Questions
- Interaction with columnar formats?
- Predicate pushdown vs projection pushdown?
- Any case where early select hurts?

---

## 33) Idempotent Batch Write Pattern

### Question
How do you make Spark batch writes idempotent?

### Why Interviewers Ask This
Reliability in reruns/backfills.

### Approach / Thought Process
1. Use deterministic keys.
2. Overwrite partition or merge on key.
3. Track run metadata.

### Answer (Detailed)
Patterns:
- Partition overwrite (`replaceWhere`) for target date.
- MERGE using natural/business key.
- Dedup source before write.
- Maintain run audit table to prevent duplicate publish.

### Follow-Up Questions
- Difference overwrite vs merge cost?
- How to handle partial failure mid-write?
- Atomicity guarantees in your storage layer?

---

## 34) Join Reordering and CBO

### Question
How does cost-based optimizer influence joins?

### Why Interviewers Ask This
Advanced query planning understanding.

### Approach / Thought Process
1. Stats-driven decisions.
2. Join reordering.
3. Importance of accurate table statistics.

### Answer (Detailed)
CBO uses row count, size, NDV stats to:
- Reorder joins for lower intermediate cardinality.
- Choose join strategy.
Bad or missing stats can produce poor plans. Collect/analyze stats regularly in warehouse/lakehouse metadata.

### Follow-Up Questions
- How to inspect whether CBO used?
- Stats collection strategy?
- AQE vs CBO relationship?

---

## 35) Streaming Deduplication

### Question
How to deduplicate streaming events in Spark?

### Why Interviewers Ask This
Exactly-once-ish processing and event integrity.

### Approach / Thought Process
1. Define event key.
2. Use watermark + dropDuplicates.
3. Ensure checkpointing.

### Answer (Detailed)
```python
deduped = stream_df \
  .withWater<read_file>
<path>data
