# 🔄 Schema Evolution

## 1. Concept Explanation

**Schema Changes Kill Pipelines:**
```
Add column → Pipeline breaks
Delete column → NULL explosions
Type change → Cast failures

Reality: Schema changes weekly in prod
```

**Compatibility Types:**
| Type | Forward | Backward | Example |
|------|---------|----------|---------|
| FULL | ✅ | ✅ | Add optional field |
| FORWARD | ✅ | ❌ | Delete field |
| BACKWARD | ❌ | ✅ | Add required field |
| NONE | ❌ | ❌ | Type change |

**Avro Schema Registry Flow:**
```
Producer → Registry check → Publish
Consumer → Registry → Evolve
```

## 2. Real-World Example - Uber

```
Event: {"ride_id":1, "price":25.5}
v2: {"ride_id":1, "price":25.5, "surge":1.2}
→ No reprocessing needed
```

## 3. Practical Scenario

**Amazon Product Feed:**
```
Daily: 1M products schema changes monthly
Schema Registry + Avro = Zero downtime
Fallback: Spark schema merge
```

## 4. Common Mistakes

| Mistake | Impact | Fix |
|---------|--------|-----|
| No registry | Manual coordination | Confluent Schema Registry |
| Breaking changes | Pipeline failures | FULL compatibility |
| JSON evolution | Schema drift | Avro/Protobuf |
| Ignore defaults | NULL floods | Default values |

## 5. Performance Tips

```
🏆 Evolution Tier List:
S-Tier: Avro + Registry
A-Tier: Protobuf
B-Tier: Spark schema merge
F-Tier: Manual JSON parsing
```

**Spark Code:**
```python
df = spark.read \
  .option("mergeSchema", "true") \
  .parquet("s3://evolving/")
```

## 6. 🔥 Interview Questions

### Amazon L5
**Q1: Handle schema changes in production pipelines?**
```
A: Schema Registry + FULL compatibility
   Spark mergeSchema for batch
```

**Q2 Follow-up: Breaking change detected. Rollback?**
```
A: Registry blocks publish → 
   Deploy old version → Fix schema
```

### Uber L4
**Q3: Streaming schema evolution?**
```
A: Kafka + Schema Registry + Avro
   Exactly-once + evolution
```

**Q4: JSON schema drift. Fix?**
```
A: 1. Sample + infer 2. Alert on drift
   3. Quarantine bad data
```

### Flipkart Scenario
**Q5: Partner feed added 'discount' field**
```
A: Avro default null → No code change
   Update consumer gradually
```

**Q6: Forward vs backward compatibility?**
```
A: Forward: New consumers read old data
   Backward: Old consumers read new data
   FULL: Both
```

---

**⚡ Pro Tip:** Schema Registry = Zero-downtime evolution.
