# 🗂️ Partitioning + Bucketing

## 1. Concept Explanation

**Partitioning:** Directory-level (date=2024/city=blr)
**Bucketing:** Hash-based within partition (user_id % 10)

**Combo Power:**
```
Partition: Prune 99% directories
Bucket: Even data distribution
Result: Perfect JOIN performance
```

**When Bucketing:**
```
High cardinality + JOINs
Skewed data
Hive/Spark SQL performance
```

## 2. Real-World Example - Amazon

```
Amazon Orders (1B/day):
PARTITIONED BY (dt, marketplace)
BUCKETS 32 (customer_id)

JOIN orders × customers:
→ Co-located buckets = 100x speedup
```

## 3. Practical Scenario

**Uber Ride Matching:**
```
Table: rides PARTITIONED BY (date) CLUSTERED BY (driver_id) INTO 64 BUCKETS

Spark JOIN rides × drivers:
→ Bucket map-join (no shuffle)
```

## 4. Common Mistakes

| Mistake | Impact | Fix |
|---------|--------|-----|
| Wrong bucket count | Skew | 32-128 buckets |
| No same column bucketing | Shuffle JOIN | Bucket same JOIN keys |
| Bucket high cardinality | Too many files | Low-cardinality keys |
| Forget SORT BY | Unordered | SORT BY within bucket |

## 5. Performance Tips

```
🏆 Bucketing Rule:
Optimal: 128MB-1GB per bucket-file

Code:
```sql
CREATE TABLE orders (
  order_id BIGINT
) PARTITIONED BY (dt STRING)
CLUSTERED BY (customer_id) INTO 64 BUCKETS
STORED AS PARQUET;
```
```

## 6. 🔥 Interview Questions

### Amazon L5
**Q1: Partition vs bucketing?**
```
A: Partition: Directory pruning (low cardinality)
   Bucket: Hash distribution (high cardinality JOINs)
```

**Q2 Follow-up: Optimal bucket count?**
```
A: 32-128. Match parallelism.
   Too few → skew, too many → small files
```

### Uber L4
**Q3: Slow JOIN on 1TB tables. Fix?**
```
A: Bucket both tables on JOIN key
   Enable bucketed map-side JOIN
```

**Q4: Data skew in bucketing?**
```
A: Salt the key: customer_id % 10 + random(10)
```

### Flipkart Scenario
**Q5: Hive query slow despite partitioning**
```
A: High-cardinality partition → Use bucketing
   CLUSTERED BY (seller_id) INTO 64
```

**Q6: Spark vs Hive bucketing?**
```
A: Spark: Automatic (sort-merge)
   Hive: Manual bucket map-joins
```

---

**⚡ Pro Tip:** Bucket JOIN keys. Instant 10x speedup.
