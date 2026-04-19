# ✅ Data Quality & Validation

## 1. Concept Explanation

**Garbage In = Garbage Out x1000**
```
1% bad data = $1M wrong decisions
DE owns data quality (not DS)

Reality: 80% DE time = data cleaning
```

**Quality Dimensions:**
| Dimension | Check | Example |
|-----------|-------|---------|
| Completeness | NULL checks | 99% email filled |
| Accuracy | Range validation | age 0-120 |
| Consistency | Cross-table | order_total = sum(items) |
| Timeliness | Freshness | <1hr delay |
| Uniqueness | Duplicates | No dup order_id |

## 2. Real-World Example - Swiggy

```
Order Pipeline:
Raw → Validation (Great Expectations) → Clean
Fail: 2% orders missing restaurant_id
Action: Alert + quarantine
```

## 3. Practical Scenario

**Amazon Inventory Sync:**
```
1. Schema validation (JSONSchema)
2. Range checks (price >0)
3. Referential integrity (product exists)
4. Freshness SLA (<5min)
```

## 4. Common Mistakes

| Mistake | Impact | Fix |
|---------|--------|-----|
| No validation | Downstream failures | Pipeline gates |
| Alert fatigue | Ignored alerts | Smart thresholds |
| Manual checks | Scale impossible | Automated tests |
| No quarantine | Poisoned tables | Dead letter queue |

## 5. Performance Tips

```
Tools Tier List:
S-Tier: Great Expectations + Airflow
A-Tier: Deequ (Spark)
B-Tier: Custom PySpark
F-Tier: Manual SQL
```

**Code Example:**
```python
# Great Expectations
expectation_suite = {
    "expect_column_values_to_not_be_null": ["order_id"],
    "expect_column_values_to_be_between": {"price": [0, 100000]}
}
```

## 6. 🔥 Interview Questions

### Amazon L5
**Q1: Ensure data quality in pipelines?**
```
A: 1. Schema enforcement 2. Quality gates
   3. Monitoring + alerts 4. Quarantine bad data
```

**Q2 Follow-up: Quality check failed production. Handle?**
```
A: Rollback + alert → Root cause (schema drift?)
   → Add test → Reprocess
```

### Uber L4
**Q3: Detect duplicate orders real-time?**
```
A: Streaming dedup (Flink state) + 
   Bloom filter for 1B keys
```

**Q4: 1% data corrupt daily. Fix systematically?**
```
A: Implement DQ framework (Deequ)
   SLO: 99.9% pass rate
```

### Netflix Scenario
**Q5: Viewing data freshness SLA broken**
```
A: Latency monitoring (Prometheus)
   Alert if >5min end-to-end
   Auto-scale Spark
```

**Q6: Schema enforcement streaming?**
```
A: Schema registry (Confluent) +
   Validation at Kafka ingress
```

---

**⚡ Pro Tip:** Quality first = trust forever.
