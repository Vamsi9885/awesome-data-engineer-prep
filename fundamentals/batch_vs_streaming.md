# ⚡ Batch vs Streaming

## 1. Concept Explanation

**Decision Matrix:**
```
Latency <5min? → Streaming
Cost >$1000/day? → Batch
Exactly-once? → Streaming (Flink)
At-least-once OK? → Spark Streaming
```

**Comparison:**
| Aspect | Batch | Streaming |
|--------|-------|-----------|
| Latency | Hours | Seconds |
| Cost | $0.10/GB | $1/GB |
| Fault Tolerance | Restart from checkpoint | Continuous |
| State | Stateless | Stateful (windows) |
| Tools | Spark/Airflow | Flink/Kafka Streams |

**Streaming Guarantees:**
```
At-least-once: Duplicates OK
Exactly-once: No duplicates (Flink)
Effectively-once: Idempotent sinks
```

## 2. Real-World Example - Uber

```
Uber Surge Pricing (real-time):
Kafka → Flink (1s latency) → DynamoDB
Batch: Daily reports Spark → Redshift

Why streaming? Price changes every 30s
```

## 3. Practical Scenario

**Netflix Recommendations:**
```
Streaming: Viewing events → Real-time features
Batch: Daily model retraining → New model
Hybrid: 80% streaming, 20% batch
```

## 4. Common Mistakes

| Mistake | Impact | Fix |
|---------|--------|-----|
| Streaming everything | 10x cost | Hybrid approach |
| No watermarking | Infinite state | Event time + watermarks |
| At-least-once to DB | Duplicates | Idempotent upserts |
| Micro-batching | 1min latency | True streaming (Flink) |

## 5. Performance Tips

```
🏆 Streaming Tier List:
S-Tier: Flink (exactly-once)
A-Tier: Spark Structured Streaming
B-Tier: Kafka Streams
F-Tier: Raw Kafka consumers

Cost: Batch $100/day → Streaming $2000/day
```

## 6. 🔥 Interview Questions

### Amazon L5
**Q1: When streaming over batch?**
```
A: Real-time SLAs (<5min), fraud detection, surge pricing
   Batch: Cost-sensitive reports, ML training
```

**Q2 Follow-up: Exactly-once implementation?**
```
A: Flink checkpointing + idempotent sinks (upsert)
   Transactional outbox pattern
```

### Uber L4
**Q3: Design real-time Uber ride pricing**
```
A: Kafka→Flink (windowed agg)→DynamoDB
   Watermarks + late data handling
```

**Q4: Streaming job OOM. Fix?**
```
A: 1. Increase parallelism 2. Smaller windows
   3. State backend tuning 4. Backpressure
```

### Swiggy Scenario
**Q5: Order ETA streaming pipeline failed**
```
A: Watermarks too aggressive → Late data dropped
   Fix: Event-time + 5min allowed lateness
```

**Q6: Micro-batch vs true streaming?**
```
A: Spark micro-batch: 100ms-1s latency
   Flink: Sub-second true streaming
```

---

**⚡ Pro Tip:** Start batch, optimize to streaming only if SLA requires.
