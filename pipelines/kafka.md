# 📡 Kafka for Data Pipelines

## 1. Concept Explanation

**Kafka = Streaming Backbone (90% prod systems)**

```
Batch: File → Spark → DB (hours)
Kafka: Event → Stream → DB (seconds)

Log-based messaging = Exactly-once + Replayable
```

**Core Concepts:**
- **Topics** = Event streams
- **Partitions** = Parallelism
- **Consumer groups** = Load balancing
- **Offsets** = Replay capability

## 2. Real-World Example - Uber Event Streaming

```
Uber Architecture:
Mobile app → Kafka (ride events) → 
Flink (real-time) + Spark (batch) → 
ClickHouse (analytics)

Scale: 10K events/sec sustained
```

## 3. Code Examples

### Kafka + Spark Streaming (Production)
```python
# Consumer config
kafka_conf = {
    'kafka.bootstrap.servers': 'kafka-cluster:9092',
    'subscribe': 'uber.ride.events',
    'startingOffsets': 'latest',
    'kafka.group.id': 'uber-analytics-group'
}

# Structured Streaming
df = spark \
    .readStream \
    .format("kafka") \
    .options(**kafka_conf) \
    .load()

# Parse + process
ride_events = df.select(
    from_json(col("value").cast("string"), ride_schema).alias("ride")
).select("ride.*")

# Output (exactly-once)
query = ride_events.writeStream \
    .format("delta") \
    .option("checkpointLocation", "s3://checkpoints/rides") \
    .partitionBy("ride_date") \
    .table("uber_bronze.rides")
```

### Kafka Producer (Python)
```python
from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers='kafka:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    retries=3,
    acks='all'  # Exactly-once
)

# Produce ride event
producer.send('uber.ride.events', {
    'ride_id': '123',
    'driver_id': 456,
    'event_time': '2024-01-15T10:30:00Z',
    'event_type': 'ride_started'
})
```

## 4. Real-Time Production Scenario

**Swiggy Order Streaming (1M orders/day):**

```
Pipeline:
Frontend → Kafka (orders) → 
Kafka Streams (routing) → 
Spark Streaming (analytics) → 
Redis (cache) + BigQuery

Metrics:
- Throughput: 15K/sec peak
- Latency: P99 < 200ms
- Durability: 7 day retention
```

## 5. Common Mistakes

| Mistake | Symptom | Fix |
|---------|---------|-----|
| 1 replica | Data loss | min.insync.replicas=3 |
| No retention | Disk full | log.retention.hours=168 |
| Single partition | No parallelism | 10-50 partitions/topic |
| At-least-once | Duplicates | Exactly-once semantics |

## 6. Production Checklist

```
🏆 Kafka Production Config:

Topic Config:
replication.factor=3
min.insync.replicas=2
retention.ms=604800000 (7 days)
cleanup.policy=delete

Consumer:
max.poll.records=500
session.timeout.ms=30000
enable.auto.commit=false  # Manual commit!

Cluster:
3+ brokers
Zookeeper ensemble
JMX monitoring
```

## 7. 🔥 Interview Questions

### Amazon L5 (Kafka Heavy)
**Q1: Exactly-once processing.**
```
A: 
Producer: acks=all + retries
Consumer: Idempotent processing + offsets
Stream: Checkpointing
```

**Q2: Consumer lag 1M messages.**
```
A: 
1. Add consumers (scale group)
2. Increase partitions
3. Batch processing
4. Prefetch tuning
```

### Uber L4
**Q3: Topic partitioning strategy.**
```
10-50 partitions/topic
Rule: consumers * 2 < partitions
Monitor: Consumer lag
```

**Q4: Schema evolution.**
```
Avro + Schema Registry
Backward/forward compatible
No breaking changes
```

### Flipkart Streaming
**Q5: Kafka Streams vs Flink vs Spark Streaming.**
```
Kafka Streams: Simple, Kafka-only
Flink: State, exactly-once, low latency
Spark: Batch+stream unification
```

**Q6: Disaster recovery.**
```
A: 
1. Cross-DC replication (MirrorMaker)
2. Consumer offset reset
3. Tiered storage (remote retention)
```

---

**📊 Pro Tip:** Kafka Manager + Prometheus = Monitor consumer lag 24/7
```
Lag > 1hr = PagerDuty NOW
