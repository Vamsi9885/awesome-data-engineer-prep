# 🌊 PySpark Structured Streaming

## 1. Concept Explanation

**Batch is dead. Streaming = future.**

```
Batch: Daily files → Yesterday's insights
Streaming: Real-time events → Now insights

Exactly-once + SQL = Production ready
```

**Core Concepts:**
- **Continuous triggers** (1s latency)
- **Watermarks** (late data handling)
- **Stateful aggregations** (sessionization)
- **Checkpointing** (fault tolerance)

## 2. Real-World Example - Uber Real-time Pricing

```
Input: Kafka (ride events/sec)
Processing: Dynamic pricing model
Output: Redis (pricing cache)
Latency: P99 < 500ms
```

## 3. Code Examples

### Complete Production Pipeline
```python
# Uber ride pricing stream
kafka_df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "ride-events") \
    .load()

# Parse + schema enforcement
ride_events = kafka_df.select(
    from_json(col("value").cast("string"), ride_schema).alias("data")
).select("data.*") \
 .withWatermark("event_time", "10 minutes")

# Stateful aggregation (1hr windows)
pricing_updates = ride_events \
    .groupBy(
        window("event_time", "1 hour"),
        "city",
        "surge_multiplier"
    ) \
    .agg(count("*").alias("ride_count"))

# Sink to Kafka (exactly-once)
query = pricing_updates \
    .writeStream \
    .format("kafka") \
    .option("checkpointLocation", "/checkpoints/pricing") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("topic", "pricing-updates") \
    .trigger(processingTime="30 seconds") \
    .start()

query.awaitTermination()
```

### Sessionization (Most Asked!)
```python
# User sessions (10min inactivity)
sessions = events \
    .withWatermark("timestamp", "10 minutes") \
    .groupBy(
        "user_id",
        session_window("timestamp", "10 minutes", "10 minutes")
    ) \
    .agg(sum("duration").alias("session_duration"))
```

## 4. Real-Time Production Scenario

**Swiggy Order Tracking (1M orders/day):**

```
Architecture:
Kafka (orders) → Spark Streaming → Redis + S3
1. Watermark: 5min (handle late GPS)
2. State: Driver locations (RocksDB)
3. Output: ETA predictions

Metrics:
- Input: 10K/sec
- Processing: 9K/sec  
- Latency: P99 < 3s
- Uptime: 99.99%
```

## 5. Common Mistakes

| Mistake | Result | Fix |
|---------|--------|-----|
| No watermark | State explosion | Always watermark |
| No checkpoint | Restart = reprocess | HDFS/S3 checkpoint |
| Memory sink | OOM | Kafka/Delta |
| Fixed trigger | Backpressure | Continuous/Adaptive |

## 6. Performance Tips

```
🏆 Streaming Best Practices:

1. Watermark = state eviction policy
2. Multiple streaming queries (decouple)
3. State cleanup (TTL)
4. Kafka consumer groups

Triggers:
- processingTime="10s" (default)
- continuous="1s" (ultra low latency) 
- once=True (batch fallback)

Checkpoint = Your safety net:
s3://checkpoints/streaming-job/
```

## 7. 🔥 Interview Questions

### Amazon L5
**Q1: Late data handling?**
```
A: Watermark + drop/allow late
.withWatermark("event_time", "1 hour")
.filter(col("event_time") >= watermark)
```

**Q2: Exactly-once guarantee?**
```
A: Checkpoint + idempotent sinks (Delta/Kafka)
No checkpoint = at-least-once only
```

### Uber L4
**Q3: 1M events/sec backpressure.**
```
A: 
1. Increase watermark
2. Multiple consumer groups
3. Separate micro-batches
4. Continuous trigger
```

**Q4: Sessionization query?**
```python
session_window("event_time", "30 minutes", "5 minutes")
```

### Flipkart Real-time
**Q5: Streaming + batch unification?**
```
A: Structured Streaming reads files too!
spark.readStream.parquet("s3://files/")
```

**Q6: State store full (10TB).**
```
A: 
1. State TTL (spark.sql.streaming.stateStore.cleanupFilesAfter)
2. Reduce watermark
3. Multiple state stores
```

---

**⚡ Pro Tip:** Streaming = batch + time. Same DataFrame API!
```python
# This works for both:
df.writeStream...  # Streaming
df.write...        # Batch
