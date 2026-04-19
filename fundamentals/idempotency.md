# 🔁 Idempotency

## 1. Concept Explanation

**Run Twice = Same Result**
```
Non-idempotent: INSERT → Duplicates
Idempotent: UPSERT → Single record

Reality: 99% pipelines retry → Must be idempotent
```

**Idempotency Patterns:**
| Pattern | Use Case | Example |
|---------|----------|---------|
| UPSERT | Databases | ON CONFLICT DO NOTHING |
| Dedup | S3 | Unique file paths |
| Transactions | Streaming | Kafka offsets |
| Checkpoints | Spark | From last checkpoint |

## 2. Real-World Example - Netflix

```
Content Upload (1M videos/day):
Non-idempotent: Duplicate uploads
Idempotent: S3 path = video_id/version
Retry safe
```

## 3. Practical Scenario

**Uber Payment Processing:**
```
1. Kafka event → Spark → Upsert DynamoDB
2. Retry on failure → Same result
3. Transaction log for audit
```

## 4. Common Mistakes

| Mistake | Impact | Fix |
|---------|--------|-----|
| INSERT only | Duplicates | UPSERT |
| No unique keys | Data explosion | Composite PK |
| Mutable S3 paths | Lost data | Immutable + version |
| No checkpoints | Restart from beginning | Offset management |

## 5. Performance Tips

```
🏆 Idempotency Tier List:
S-Tier: Delta Lake (MERGE)
A-Tier: DynamoDB conditional writes
B-Tier: S3 atomic writes
F-Tier: Custom dedup logic
```

**Spark Idempotent Write:**
```python
df.write \
  .format("delta") \
  .mode("overwrite") \
  .option("mergeSchema", "true") \
  .saveAsTable("orders")
```

## 6. 🔥 Interview Questions

### Amazon L5
**Q1: Design idempotent Spark pipeline?**
```
A: Delta Lake MERGE + checkpointLocation
   Watermark deletes for CDC
```

**Q2 Follow-up: Streaming idempotency?**
```
A: Flink exactly-once + idempotent sink
```

### Uber L4
**Q3: Pipeline retried 3x. Duplicate data?**
```
A: Missing idempotency. Implement UPSERT
   Use transaction_id + dedup
```

**Q4: S3 write idempotent?**
```
A: Atomic S3 PUT + unique path
   video_id/date/hour/random_uuid.parquet
```

### Swiggy Scenario
**Q5: Airflow retry → Duplicate orders**
```
A: Add run_id to unique constraint
   UPSERT (run_id, order_id)
```

**Q6: Exactly-once vs idempotent?**
```
A: Exactly-once: No duplicates in stream
   Idempotent: Duplicates OK if result same
```

---

**⚡ Pro Tip:** Non-idempotent = Production nightmare.
