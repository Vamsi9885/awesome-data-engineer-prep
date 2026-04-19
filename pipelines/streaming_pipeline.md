# ⚡ Production Streaming Data Pipelines (Azure, AWS, GCP)

## 1. Concept Explanation

A **streaming pipeline** processes events continuously with low latency (seconds/sub-seconds), while preserving correctness under out-of-order, duplicate, and late-arriving data.

Production requirements:
- Event-time correctness over ingestion-time shortcuts
- Exactly-once/ effectively-once delivery to sinks
- Stateful processing with checkpointing
- Backpressure handling and autoscaling
- Replay/reprocessing with retained logs

Latency SLO examples:
- Fraud scoring < 2s P95
- Driver dispatch updates < 500ms P99
- Real-time dashboard lag < 60s

---

## 2. Architecture Flow (Text Diagrams)

### Generic Streaming Flow
```text
Producers → Event Bus → Stream Processor → Stateful Store/Lake/Warehouse → Serving Layer
```

### Azure Streaming Flow
```text
Apps/Services
  → Event Hubs
  → Databricks Structured Streaming
  → Delta Lake (bronze/silver/gold)
  → Synapse Serverless / Power BI
```

### AWS Streaming Flow
```text
Apps/IoT/Logs
  → Kinesis Data Streams
  → Lambda / Kinesis Data Analytics / Spark
  → S3 (raw) + Redshift (serving)
  → QuickSight / APIs
```

### GCP Streaming Flow
```text
Microservices / Mobile Events
  → Pub/Sub
  → Dataflow (Apache Beam)
  → BigQuery streaming tables
  → Looker / alerting services
```

---

## 3. Cloud-Specific Implementations

## Azure (Event Hubs + Databricks + Delta + Synapse)

```python
from pyspark.sql.functions import from_json, col, to_timestamp, window
from pyspark.sql.types import StructType, StringType, DoubleType

schema = StructType() \
    .add("ride_id", StringType()) \
    .add("driver_id", StringType()) \
    .add("city", StringType()) \
    .add("fare_amount", DoubleType()) \
    .add("event_time", StringType())

raw = (spark.readStream
  .format("eventhubs")
  .options(**event_hubs_conf)
  .load())

events = (raw
  .select(from_json(col("body").cast("string"), schema).alias("e"))
  .select("e.*")
  .withColumn("event_ts", to_timestamp("event_time")))

(events.writeStream
 .format("delta")
 .option("checkpointLocation", "abfss://checkpoints@lake/ride_events")
 .option("mergeSchema", "true")
 .partitionBy("city")
 .start("abfss://bronze@lake/ride_events"))
```

---

## AWS (Kinesis + Lambda + S3 + Redshift)

Design pattern:
1. Kinesis receives records partitioned by key (`customer_id`, `ride_id`).
2. Lambda transforms/validates and writes failed payloads to DLQ.
3. Firehose/Lambda sink to S3 partitioned paths.
4. Redshift COPY/MERGE publishes curated aggregates.

Key controls:
- Enhanced fan-out for high consumer concurrency
- Per-shard scaling and split/merge management
- Redshift materialized views for near-real-time analytics

---

## GCP (Pub/Sub + Dataflow + BigQuery)

Beam pattern:
- Parse + schema validate
- key-by entity
- event-time windowing + triggers
- deduplicate on event_id
- write to BigQuery with dead-letter side output

```python
# Pseudocode pattern
(
  p
  | "ReadPubSub" >> beam.io.ReadFromPubSub(topic=topic)
  | "ParseJson" >> beam.Map(parse_json)
  | "Validate" >> beam.ParDo(ValidateFn()).with_outputs("bad", main="good")
)

good_stream = ...
bad_stream  = ...  # write to DLQ
```

---

## 4. Failure Handling

Core techniques:
- **Retries with jitter** for transient sink/network errors
- **Checkpointing** (state store + offsets)
- **Dead-letter queues** for malformed records
- **Replay** from retained topic/subscription
- **Exactly-once sinks** where supported (Delta transactional writes, Beam semantics)
- **Poison-pill detection** with schema registry and validation rules

Late/out-of-order handling:
- use watermark (e.g., 10 minutes)
- keep state TTL tuned for event-time skew
- emit corrections to downstream consumers when required

---

## 5. Logging & Monitoring

### Azure Monitor
- Event Hubs incoming messages, throttles, consumer lag
- Databricks micro-batch duration, input rows/sec
- Delta table operation metrics

### AWS CloudWatch
- Kinesis iterator age
- Lambda errors/throttles/duration
- Firehose delivery failures

### GCP Cloud Monitoring (Stackdriver)
- Pub/Sub undelivered message count
- Dataflow backlog bytes, watermark age
- BigQuery streaming insert errors

Alert examples:
- P95 end-to-end lag > 120s
- error rate > 0.5% in 5 min
- DLQ volume > baseline threshold

---

## 6. Real-World Scenarios

### Ride-sharing dispatch telemetry
- Stream vehicle location + driver status events
- Windowed city heatmaps every 30s
- Late GPS packets reconciled within 5-minute watermark
- Dispatch and ETA models consume gold streaming table

### E-commerce clickstream and orders
- Ingest page views, cart events, checkout events
- Sessionize by user + inactivity gap
- Real-time funnel drop-off alerts
- Persist raw for replay + offline attribution models

---

## 7. Common Mistakes

1. Using processing-time only; incorrect business metrics.
2. No watermark; state grows unbounded.
3. No dedup key; duplicates inflate KPIs.
4. Tiny micro-batches causing high overhead.
5. Ignoring partition-key skew (hot shards/partitions).
6. No DLQ; bad events crash whole pipeline.
7. No replay runbook for incident recovery.

---

## 8. Performance Tips

- Select partition keys with even cardinality.
- Tune trigger intervals (not too tiny).
- Use column pruning and projection early.
- Use stateful ops only where required.
- Compact streaming output files periodically.
- Separate hot-path and cold-path consumers.
- Pre-aggregate before warehouse sink when possible.
- Monitor lag + autoscale before saturation.

---

## 9. 🔥 Interview Questions (Streaming)

### Q1. What is idempotency in streaming?
Idempotency means reprocessing or duplicate delivery does not change final output multiple times. Use event IDs + dedup state + upsert sinks.

### Q2. How do you handle late-arriving data?
Use event-time windows with watermark; allow bounded lateness and emit updates/corrections to downstream aggregates.

### Q3. What is exactly-once processing?
Exactly-once means each logical event affects sink state once, despite retries/failures. Achieved with transactional sinks, checkpointed offsets, and deterministic processing.

### Q4. How do you design fault-tolerant streaming pipelines?
Decouple ingestion/processing/sink, checkpoint state, apply retries with backoff, isolate bad events to DLQ, and support replay from retained logs.

### Additional prompts
- Event-time vs processing-time: when to choose each?
- How do you mitigate hot partitions in Kinesis/Kafka/PubSub?
- How do you roll out schema changes without downtime?
- How do you recover from corrupted state store/checkpoint?
