# Architecture — Real-Time Ride Tracking System (Uber-like)

## Text-Based Architecture Diagram

```text
Mobile Apps / Driver Apps
        │
        │ events (protobuf/json)
        ▼
┌────────────────────────────────────────────────────────────────┐
│  Ingestion Layer (interchangeable by cloud)                  │
│  AWS: Kinesis  |  Azure: Event Hubs  |  GCP: Pub/Sub         │
└───────────────┬───────────────────────────────────────────────┘
                │
                ▼
      ┌──────────────────────────┐
      │ Spark Structured Streaming│
      │ - event-time windows      │
      │ - watermarking            │
      │ - stateful trip machine   │
      │ - dedupe + enrichment     │
      └─────────────┬────────────┘
                    │
        ┌───────────┼───────────────────┐
        ▼           ▼                   ▼
┌─────────────┐ ┌───────────────┐ ┌──────────────────┐
│ Bronze Delta│ │ Silver Delta  │ │ Dead-letter Delta│
│ raw immutable││ conformed/live │ │ parse/schema errs│
└──────┬──────┘ └───────┬───────┘ └──────────────────┘
       │                │
       ▼                ▼
┌──────────────────────────────┐
│ Gold Serving Tables           │
│ - active_rides_by_city        │
│ - eta_metrics_1min            │
│ - cancellation_rate_5min      │
│ - driver_utilization_5min     │
└──────────────┬───────────────┘
               │
               ▼
      Dashboards + Alerting + APIs
      (Ops, Dispatch, Trust & Safety)
```

---

## Core Components

1. **Ingress abstraction**
   - A connector layer allows switching between Kafka/Kinesis/Event Hubs/PubSub with minimal pipeline code changes.

2. **Stateful streaming processor**
   - Maintains per-trip state keyed by `ride_id`.
   - Handles event sequence correctness with event-time semantics.

3. **Medallion storage**
   - Bronze for replayability.
   - Silver for cleansed and deduplicated event stream.
   - Gold for low-latency operational metrics.

4. **Observability**
   - Streaming query progress metrics.
   - Lag and throughput alerting.
   - DLQ volume anomaly alarms.

---

## Why This Architecture

- **Supports low latency and correctness simultaneously**
  - event-time + watermarks protect against out-of-order events.
- **Replay and auditability**
  - immutable bronze allows deterministic recovery and post-incident replay.
- **Cross-cloud portability**
  - ingress abstraction enables region-by-region platform choice.
- **Scalability**
  - micro-batch scaling with adaptive shuffle and autoscaling executors.

---

## Design Trade-offs

- Spark streaming vs Flink/Dataflow:
  - Spark chosen for team familiarity and unified batch + stream stack.
  - Flink offers lower-latency fine-grained state control but higher operational complexity for this team.
- Delta sink vs direct dashboard DB writes:
  - Delta gives transactional reliability and replayability.
  - direct writes reduce hop latency but weaken recoverability and lineage.

---

## Failure Handling

- Checkpoint + WAL-backed structured streaming offsets.
- Exactly-once sink semantics through idempotent upsert keys.
- On failure:
  1. restart from checkpoints
  2. rerun impacted watermark horizon windows
  3. reconcile metric parity vs control tables

---

## Scaling Strategy (10x)

- shard by `(city_id, ride_id_hash_mod_n)` to reduce hot partitions
- pre-aggregate noisy location pings at edge before core stream
- adaptive query execution and dynamic state timeout tuning
- separate high-priority city streams into dedicated consumer groups

---

## Security & Governance

- tokenized passenger and driver IDs in silver/gold
- RBAC by domain (dispatch/finance/trust-safety)
- end-to-end encrypted transport and storage
- immutable audit logs for compliance review

---

## Interview Questions (Architecture Focus)

1. How does watermark duration impact both correctness and latency?
2. What if one city’s event rate is 20x others?
3. How would you redesign this for sub-second SLA?
4. How do you prove no duplicate state transitions for a ride?
