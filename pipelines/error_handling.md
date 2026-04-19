# 🚨 Error Handling for Production Data Pipelines

## 1. Concept Explanation

Error handling in data pipelines is not just `try/except`; it is a full reliability framework covering:
- detection
- classification
- containment
- recovery
- prevention

Failure classes:
1. **Transient** (network timeout, temporary throttling)
2. **Data quality** (null keys, schema mismatch, referential break)
3. **Systemic** (dependency outage, credential failure)
4. **Logic errors** (bad transform/deployment bug)

A mature pipeline distinguishes these classes and responds differently.

---

## 2. Architecture Flow (Text Diagram)

```text
Ingestion → Validation → Transformation → Publish
    |           |             |            |
    |           └── bad rows → Quarantine/DLQ
    |                         |
    └──────── retry/backoff ─┘
                    |
              Alerts + Runbook
                    |
              Replay/Backfill
```

Cross-cloud variant:
```text
Source → (ADF / Glue / Dataflow) → Lake/Warehouse
         + Retry Policy + Checkpoint + DLQ + Monitoring + On-call Alerts
```

---

## 3. Cloud-Specific Implementations

## Azure
- ADF retry policy per activity
- Databricks structured logging + checkpoint directories
- ADLS quarantine zone (`/quarantine/{table}/date=...`)
- Azure Monitor alerts + Action Groups

## AWS
- Glue/EMR retries + Step Functions catch/retry branches
- SQS DLQ for Lambda-driven ingestion
- CloudWatch metric filters and alarms
- Redshift load error table audits

## GCP
- Dataflow dead-letter side outputs
- Pub/Sub subscription retry and dead-letter topics
- Cloud Monitoring alerts and Error Reporting
- BigQuery rejected rows table patterns

---

## 4. Failure Handling Patterns

## Retry Logic
Use exponential backoff + jitter:
- 1st retry: 30s
- 2nd retry: 2m
- 3rd retry: 10m
- then route to manual intervention

Do not retry permanent errors infinitely (e.g., schema incompatibility).

## Checkpoints
Persist:
- offsets / subscription ack IDs
- processed file manifests
- watermark tables
- batch run IDs and row counts

Checkpoint goals:
- resume from last consistent point
- avoid duplicate processing

## Dead-Letter Queues
Route records that fail validation/parsing/business rules to DLQ:
- include error reason and payload hash
- include producer metadata
- ensure triage tooling and replay utility exist

---

## 5. Logging & Monitoring

Minimum observability contract:
- `pipeline_name`, `run_id`, `step`, `source`, `target`
- `records_read`, `records_written`, `records_failed`
- error codes and stack traces
- latency and resource utilization

Cloud tools:
- Azure Monitor + Log Analytics
- AWS CloudWatch + X-Ray (where relevant)
- GCP Cloud Logging + Cloud Monitoring (Stackdriver)

Recommended alerts:
- SLA breach (data freshness)
- error-rate threshold
- repeated retries exhausted
- DLQ spike anomaly

---

## 6. Real-World Scenarios

### Uber ride event ingestion
Issue: malformed events from one app version caused parser failures.
Handling:
- route bad payloads to DLQ by app_version
- continue healthy traffic path
- hotfix parser, replay DLQ subset
Result: no full-stream outage, bounded data loss window.

### E-commerce order ETL
Issue: source added `discount_type` column breaking strict schema.
Handling:
- schema evolution checks in bronze
- backward-compatible transform logic
- quarantine incompatible records
- alert data platform channel
Result: pipeline stayed up; partial data quarantined and reconciled later.

---

## 7. Common Mistakes

1. Treating all errors as retryable.
2. Crashing pipeline on single bad record.
3. No DLQ metadata for root-cause analysis.
4. Logging without correlation IDs/run IDs.
5. No reconciliation after incident recovery.
6. No test for schema drift.
7. Coupling alerting directly to transform code.

---

## 8. Performance Tips (with Reliability)

- Validate schema early to fail fast.
- Use vectorized validation for batch workloads.
- Keep quarantine writes asynchronous.
- Avoid expensive per-record remote calls in hot paths.
- Limit exception stack generation in tight loops.
- Sample verbose logs under high throughput.
- Pre-compute DQ checks on partition boundaries.

---

## 9. 🔥 Interview Questions (Error Handling)

### Q1. What is idempotency and why is it critical for error recovery?
Idempotency ensures reruns after failure don’t create duplicate side effects. Recovery and retries are safe only when writes are idempotent.

### Q2. How do you handle late-arriving data with failures?
Keep mutable windows and correction jobs. Late records that fail validation go to DLQ/quarantine and are replayed after fix, preserving event-time correctness.

### Q3. What is exactly-once processing under failure?
Exactly-once requires coordinated checkpoint + transactional write + deterministic dedup logic. At-least-once delivery can still produce exactly-once outcomes with idempotent sink behavior.

### Q4. How do you design fault-tolerant pipelines?
Classify errors, isolate bad records, use retries for transient faults, durable checkpoints for resume, DLQ for poison records, and runbooks for replay/reconciliation.

### Additional prompts
- How do you alert without creating pager fatigue?
- How do you replay only failed partitions safely?
- How do you test chaos scenarios in data pipelines?
- What metrics prove reliability improved over time?
