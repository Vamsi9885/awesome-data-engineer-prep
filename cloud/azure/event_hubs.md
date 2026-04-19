# Azure Event Hubs

## 1) What is the Service?
Azure Event Hubs is a high-throughput event ingestion platform for streaming data.  
It is Azure’s managed equivalent in the Kafka/Kinesis class for telemetry, logs, clickstream, IoT, and operational events.

---

## 2) When to Use?
Use Event Hubs when you need:
- Massive event ingestion (high messages/sec)
- Durable partitioned stream for downstream consumers
- Low-latency pipeline feeding analytics and alerting
- Kafka protocol compatibility in Azure ecosystems

---

## 3) Architecture Usage
Role in pipeline:
- Entry point for real-time events
- Producers push events to topic/hub partitions
- Consumers (Databricks, ASA, Functions) process stream
- Sink to ADLS/Synapse/Cosmos/alerts

### Streaming Architecture (Azure)
`Apps/Devices → Event Hubs → Databricks/ASA → ADLS/Synapse/Power BI`

---

## 4) Real-World Example
### Uber-like Trip Events
- Driver app events (location, ride-state, fare updates)
- Event Hubs buffers bursts during peak city traffic
- Streaming jobs compute ETA and surge indicators in near real-time

### Netflix-like Playback Telemetry
- Playback start/stop/buffering events stream continuously
- Real-time quality metrics and anomaly alerts generated

---

## 5) Integration with Other Services
- **Databricks Structured Streaming** for advanced real-time ETL
- **Azure Stream Analytics** for SQL-like stream transformations
- **Azure Functions** for lightweight event-driven actions
- **ADLS** for raw stream archival
- **Synapse** for analytics consumption
- **Kafka clients** via Event Hubs Kafka endpoint

---

## 6) Common Mistakes
1. Under-partitioning (consumer bottlenecks)
2. No idempotency/dedup downstream
3. Very short retention for recovery use-cases
4. Not planning consumer group strategy
5. Ignoring ordering semantics within partition only

---

## 7) Performance Tips
- Pick partition count based on consumer parallelism and key distribution
- Use stable partition keys (e.g., user_id/device_id) when order matters
- Batch producer sends for better throughput
- Monitor lag, throttling, and ingress/egress metrics
- Use Capture to archive raw events into ADLS automatically
- Separate critical and non-critical streams into distinct hubs/namespaces

### Cost Tips
- Right-size throughput units/processing units
- Avoid over-retention if long replay is not required
- Compress payload where practical

---

## 8) 🔥 Interview Questions

### Conceptual
1. How does Event Hubs partitioning work?
2. What ordering guarantees does Event Hubs provide?
3. Event Hubs vs message queue—what’s the difference?

### Scenario-Based
4. Consumer lag keeps increasing during traffic spikes. How do you fix?
5. How would you replay last 6 hours of events after a downstream failure?
6. How do you handle duplicate events in downstream aggregates?

### Product/Comparison
7. **Event Hubs vs Kafka**
   - Event Hubs: managed service, Azure integration, less ops
   - Kafka: full control and ecosystem depth, more operational burden
8. **Kinesis vs Event Hubs vs Pub/Sub**
   - Similar stream-ingestion role; differ in scaling model, ecosystem and ops experience

### Follow-up
9. How many partitions for 200MB/s ingest with 20 consumers?
10. When would you choose Stream Analytics over Databricks for Event Hubs processing?
