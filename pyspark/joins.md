# 🔗 PySpark Joins (Strategy, Internals, and Interview Depth)

---

## 1) Concept Explanation

Joins are often the **most expensive** operation in Spark pipelines.

Join performance depends on:
- dataset sizes
- key cardinality/skew
- partitioning
- selected physical strategy

Core join strategies to know:
1. **Broadcast Hash Join (BHJ)**
2. **Shuffle Hash Join (SHJ)**
3. **Sort Merge Join (SMJ)**

Join types (business semantics):
- inner
- left/right/full outer
- left_semi
- left_anti

---

## 2) PySpark Code Examples (Real-World)

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import broadcast, col

spark = SparkSession.builder.appName("joins-demo").getOrCreate()

trips = spark.read.parquet("s3://lake/fact/trips/")          # very large
drivers = spark.read.parquet("s3://lake/dim/drivers/")       # small-medium
cities = spark.read.parquet("s3://lake/dim/cities/")         # small
```

### A) Broadcast Join (small dimension)
```python
enriched = trips.join(broadcast(cities), "city_id", "left")
```

### B) Standard join (may become SMJ/SHJ based on plan)
```python
trip_driver = trips.join(drivers, "driver_id", "inner")
```

### C) Semi/Anti joins (highly useful in ETL)
```python
# Keep only records with existing drivers
valid_trips = trips.join(drivers.select("driver_id"), "driver_id", "left_semi")

# Identify orphan records
orphan_trips = trips.join(drivers.select("driver_id"), "driver_id", "left_anti")
```

### D) Join hints
```python
hinted = trips.hint("merge").join(drivers.hint("merge"), "driver_id")
```

---

## 3) DAG Explanation

Example flow:
`read trips -> filter -> join drivers -> groupBy city -> write`

```text
Stage 1:
  Scan/filter trips

Stage 2:
  Scan drivers
  If broadcast: ship small table to executors (no large shuffle join)

Stage 3:
  Join execution
  - SMJ/SHJ => shuffle-heavy stage
  - BHJ => lower shuffle cost

Stage 4:
  groupBy city (shuffle)

Stage 5:
  write output
```

Join choice can change stage count and shuffle volume significantly.

---

## 4) Spark Internals (Basic → Moderate)

How Spark decides join strategy:
- Statistics (table size, row count)
- `spark.sql.autoBroadcastJoinThreshold`
- Join condition type
- AQE runtime statistics

Typical physical operators:
- `BroadcastHashJoinExec`
- `SortMergeJoinExec`
- `ShuffledHashJoinExec`

Inspection:
```python
trip_driver.explain("formatted")
```
Look for:
- `BroadcastExchange`
- `Exchange hashpartitioning(...)`
- Sort operators before merge join

### Strategy characteristics

## Broadcast Hash Join
- Best when one side is small (dimension table)
- Avoids large shuffle on big table
- Fastest for star-schema style joins

## Sort Merge Join
- Common default for large-large equi joins
- Requires shuffle + sort on both sides
- Stable and scalable but expensive

## Shuffle Hash Join
- Hash-based after shuffle
- Can be good in specific size distributions
- Less common than SMJ in many setups

---

## 5) Real-World Scenario

**Marketplace ETL (Amazon-style)**  
Fact table: 8 TB orders/day  
Dimensions: seller(50 MB), product(2 GB), geography(20 MB)

Optimization strategy:
- broadcast geography + seller
- avoid broadcasting product (too large)
- pre-filter fact on date/status
- join order:
  1. fact + small dims (broadcast)
  2. then fact + medium dim
- monitor skew on popular product IDs

Outcome:
- shuffle reduced ~40%
- runtime dropped from 95 min to 42 min

---

## 6) Common Mistakes

1. Joining huge datasets before filtering.
2. Blindly broadcasting table without size check.
3. Ignoring skewed keys (hot key causes straggler tasks).
4. Selecting `*` from both tables (wider rows, higher shuffle).
5. Wrong join type causing duplicate explosion.
6. Not validating join cardinality assumptions.

---

## 7) Performance Tips

- Filter and project columns before join.
- Broadcast only truly small tables.
- Tune:
  - `spark.sql.autoBroadcastJoinThreshold`
  - `spark.sql.shuffle.partitions`
- Handle skew with salting / skew hints / split strategy.
- Prefer equi-join keys with good cardinality.
- Inspect Spark UI join stage: skew, spill, task duration variance.
- Use bucketing/partition alignment in repeated heavy joins.

---

## 8) 🔥 Interview Questions

## Basic
1. What are join strategies in Spark?
2. Difference between broadcast join and shuffle join?
3. When is sort merge join used?
4. What is left_semi vs left_anti join?

## Advanced
1. How does Spark decide join strategy internally?
2. Why can broadcast join fail at runtime?
3. Explain tradeoffs between SMJ and BHJ.
4. How does AQE improve joins?

## Product Scenarios
1. 3 TB fact + 30 MB dim join is slow. What would you do?
2. Join stage has one task 15x slower than others. Diagnose and fix.
3. You must join same large tables daily. What storage design helps?

## Follow-up Questions
- Can non-equi joins use broadcast hash join?
- Why can sort before merge become bottleneck?
- How to detect wrong join strategy from `explain()`?
- What if both tables are too large to broadcast?

---

## 9) Global Cross-Questions (Required)

- **Broadcast vs shuffle join?**  
  Broadcast replicates small side and avoids large network shuffle; shuffle join redistributes both sides by key.
- **What happens during shuffle?**  
  Partition write, spill, network fetch, merge/sort, then reduce-side processing.
- **How Spark optimizes queries?**  
  Catalyst + AQE + pushdown/pruning + join re-planning at runtime.
- **Repartition vs coalesce in join pipelines?**  
  `repartition` (shuffle, increase/decrease, rebalance), `coalesce` (reduce partitions, minimal shuffle).
