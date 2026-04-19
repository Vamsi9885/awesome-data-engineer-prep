# ⚖️ Data Skew

## 1. Concept Explanation

**Skew Kills Spark Jobs:**
```
Normal: 10 tasks × 10GB = 100GB
Skewed: 9 tasks × 1GB + 1 task × 91GB = OOM

Reality: 90% Spark failures = skew
```

**Types:**
| Skew Type | Example | Impact |
|-----------|---------|--------|
| Partition | 1 partition 90% data | Slow task |
| Key | 1 user 50% orders | Reducer OOM |
| Join | Uneven tables | Shuffle explosion |

## 2. Real-World Example - Flipkart

```
Top seller = 30% orders
JOIN orders × products:
→ 1 reducer gets 300GB, others 10GB
→ OOM after 2 hours
```

## 3. Practical Scenario

**Amazon Product Reviews:**
```
1 product = 1M reviews, others 10
GROUP BY product_id → Single task OOM
```

## 4. Common Mistakes

| Mistake | Impact | Fix |
|---------|--------|-----|
| GROUP BY high-cardinality | Single reducer | Broadcast small table |
| No salting | Skewed keys | Add random salt |
| Uneven partitions | Hotspots | Repartition(200) |

## 5. Performance Tips

```
🏆 Anti-Skew Arsenal:
1. Salting: key + random(10)
2. Repartition(n) before shuffle
3. Broadcast small tables
4. AQE (Adaptive Query Execution)
```

**Salting Code:**
```python
# Skewed: customer_id
df.withColumn("salted_id", 
  concat(col("customer_id"), 
         round(rand()*10,0).cast("int")))
.groupBy("salted_id").count()
```

## 6. 🔥 Interview Questions

### Amazon L5
**Q1: Spark job stuck at 1 task 99%. Fix?**
```
A: Data skew. Check Spark UI Executors
   Fix: Salting + repartition(400)
```

**Q2 Follow-up: Detect skew proactively?**
```
A: Spark UI → Task times >5min variance
   Ganglia metrics → Partition sizes
```

### Uber L4
**Q3: GROUP BY city slow (1 city 40%)**
```
A: 1. Salt: city || random(0,9)
   2. Repartition(1000)
   3. Enable AQE
```

**Q4: Skewed JOIN strategy?**
```
A: Broadcast small table OR
   Bucket both on join key OR
   Salt join keys
```

### Swiggy Scenario
**Q5: Top 1% users = 80% orders. Handle?**
```
A: User salting + 2-phase aggregation
   Phase1: local agg, Phase2: global agg
```

**Q6: AQE vs manual skew handling?**
```
A: AQE auto-detects (Spark 3+)
   Manual for complex cases
```

---

**⚡ Pro Tip:** Always check Spark UI task times first.
