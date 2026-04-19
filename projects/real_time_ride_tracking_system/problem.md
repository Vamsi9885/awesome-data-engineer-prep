# Problem Statement — Real-Time Ride Tracking System (Uber-like)

## Business Context

A ride-hailing platform needs second-level visibility into active trips, ETAs, cancellations, and driver utilization across 120+ cities. Product, dispatch, and trust-and-safety teams depend on real-time telemetry.

Today’s pain points:
- delayed trip state updates during traffic spikes
- incorrect ETA from out-of-order GPS events
- duplicate events due to mobile retries and network flaps
- inconsistent behavior across cloud providers in different geographies

---

## Functional Requirements

1. Ingest high-volume events:
   - `ride_requested`
   - `driver_assigned`
   - `trip_started`
   - `location_ping`
   - `trip_completed`
   - `trip_canceled`
2. Process streams in near real time (<5 sec p95 processing latency).
3. Maintain trip state per ride with event-time semantics.
4. Handle late and out-of-order data safely.
5. Support interchangeable streaming ingress:
   - AWS Kinesis
   - Azure Event Hubs
   - GCP Pub/Sub
6. Persist:
   - raw events in Delta Lake (bronze)
   - deduped/enriched events in silver
   - serving aggregates for dashboards in gold
7. Provide analytics for:
   - active rides by city
   - avg pickup ETA
   - cancellation rate by segment
   - driver utilization

---

## Non-Functional Requirements

- End-to-end latency target: < 10 sec (event generated -> dashboard visible)
- Availability: 99.95%
- Exactly-once result guarantees at sink layer
- RTO: 30 min for pipeline recovery
- RPO: <= 5 min
- Security: PII tokenization, encryption in transit/at rest
- Cost controls during peak hours (Friday evenings, storms, events)

---

## Data Volumes & Constraints

- Peak incoming event rate: 2.5M events/sec globally
- Location pings dominate traffic (~88% of events)
- Hot partitions: top 10 cities can represent 45% of volume
- Mobile clients often batch-send delayed events after reconnect
- Clock skew across client devices (up to ±90 seconds)

---

## Real-World Challenges

- Data skew by city and event type
- Late-arriving data and out-of-order event-time sequences
- Duplicate handling across retries and at-least-once ingestion
- Schema evolution from mobile app releases
- Backfilling missed event windows after outages

---

## Success Criteria

1. p95 event processing latency under 5 seconds.
2. Trip-state correctness > 99.99% vs replayed truth set.
3. Duplicate event leakage to silver < 0.02%.
4. Zero data loss for recoverable infrastructure failures.
5. Interview readiness:
   - explain watermark and state timeout strategy
   - explain event-time vs processing-time trade-offs
   - explain exactly-once output with checkpointed writes

---

## Interview Questions (Project-Specific)

### Conceptual
1. Why use Spark Structured Streaming stateful processing for trip lifecycle?

### Trade-offs
2. Kafka vs Kinesis vs Event Hubs vs Pub/Sub for this use case—how do you choose?
3. Why Delta Lake for streaming sink vs direct serving DB writes?

### Scaling
4. How do you handle 10x event spikes during city-wide disruptions?

### Failure Scenarios
5. What happens when checkpoint storage is temporarily unavailable?
6. How do you recover from partial micro-batch commits?

### Optimization
7. How do you reduce state-store memory pressure?
8. How do you lower cost without violating latency SLO?
