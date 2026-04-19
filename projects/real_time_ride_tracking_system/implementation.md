# Implementation — Real-Time Ride Tracking System (Uber-like)

## 1) Pipeline Flow

1. Consume from cloud stream source (Kinesis/Event Hubs/PubSub abstraction).
2. Parse and validate event schema.
3. Write raw immutable stream to bronze Delta.
4. Deduplicate and enforce event-time ordering in silver.
5. Build stateful trip view and aggregate KPIs in gold.
6. Push serving data to dashboard cache/warehouse.

---

## 2) Event Contract

Core fields:
- `event_id STRING`
- `ride_id STRING`
- `driver_id STRING`
- `rider_id STRING`
- `city_id STRING`
- `event_type STRING`
- `event_ts TIMESTAMP`
- `ingest_ts TIMESTAMP`
- `lat DOUBLE`
- `lon DOUBLE`
- `device_ts TIMESTAMP`
- `source_platform STRING`
- `event_version INT`

Validation:
- drop/quarantine null `ride_id`, null `event_ts`, invalid `event_type`
- enforce max coordinate bounds
- contract version checks by app release

---

## 3) Event-Time + Late Data Strategy

- Watermark: `event_ts` with 15-minute lateness for operational KPIs.
- For billing-critical flows, separate stream uses 2-hour watermark.
- Out-of-order handling:
  - order per `ride_id` by `event_ts`
  - maintain finite-state-machine transitions:
    - requested -> assigned -> started -> completed/canceled

Invalid transitions are sent to exception stream with reason codes.

---

## 4) Duplicate Handling

- primary dedupe key: `event_id`
- fallback dedupe hash: `sha2(ride_id, event_type, event_ts, lat, lon, driver_id)`
- silver keeps most recent payload when duplicates conflict
- dedupe metrics emitted per city and app version

---

## 5) Stateful Processing

Trip state store keyed by `ride_id` stores:
- latest known status
- latest location
- pickup_ts, start_ts, end_ts
- cumulative distance and ETA confidence
- timeout policy for zombie rides

State eviction:
- completed/canceled rides evicted after 4 hours
- inactive rides timed out after 30 minutes with unresolved status flag

---

## 6) Storage Strategy

### Bronze
- append-only Delta
- partition: `event_date`, `city_id`

### Silver
- deduped normalized events
- partition: `event_date`, `city_id`, `event_type`

### Gold
- low-latency aggregates:
  - `gold_active_rides_1min`
  - `gold_eta_quality_5min`
  - `gold_cancellation_rate_5min`
- partition: `ds`, `city_id`

---

## 7) Performance and Scaling

- autoscaling executors (min 20, max 400)
- adaptive query execution
- selective caching for hot city dimension tables
- avoid large state by pre-aggregating location pings
- dynamic repartition by city + hash bucket to mitigate skew

---

## 8) Failure Handling & Recovery

If micro-batch fails:
1. restart query from checkpoint
2. replay uncommitted offsets
3. dedupe sink prevents double counting

If schema changes unexpectedly:
1. route incompatible events to DLQ
2. trigger schema-alert pipeline
3. roll forward contract after compatibility review

Backfill:
- replay event windows from bronze by time range
- write to shadow gold tables
- compare with production aggregates before promotion

---

## 9) Cost Optimization

- separate critical and non-critical streams into different clusters
- use spot instances for non-critical backfill
- compact silver/gold files every 30 minutes
- reduce cardinality explosion in tags/metadata columns

---

## 10) Interview Questions (Implementation Focus)

### Conceptual
1. How do you ensure correct trip status under out-of-order events?

### Trade-offs
2. Why maintain separate watermark windows for ops vs billing use cases?

### Scaling
3. How do you tune state-store size and checkpoint frequency at 10x scale?

### Failure Scenarios
4. What if a checkpoint is corrupted? What is your restore strategy?

### Optimization
5. How do you reduce processing latency without sacrificing state correctness?
