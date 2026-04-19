# Data Engineer System Design Interview Guide (Amazon/Uber/Netflix-Level)

## What Interviewers Look For
1. Requirement clarity before architecture.
2. Correctness + scalability + operability.
3. Trade-off awareness (latency/cost/consistency).
4. Failure handling and observability.
5. Practical technology choices.

## Common Mistakes
- Jump straight to tools without requirements.
- No throughput/latency sizing.
- No backfill/replay strategy.
- No schema evolution/data quality strategy.
- No failure-mode discussion.

## Pro Tips
- Start with API/contract + data model + SLA.
- Always separate ingestion, processing, serving.
- State assumptions and constraints explicitly.
- Include runbooks and monitoring.

---

## 1) Design Netflix Recommendation Data Pipeline

### 1. Problem Statement
Design a recommendation data platform supporting batch + near-real-time features for personalized ranking.

### 2. Clarifying Questions
- What latency SLA for recommendations? (e.g., <200ms serving)
- Feature freshness target? (streaming <5 min + daily batch)
- Expected scale? (100M users, billions events/day)
- Online/offline feature parity required?
- Cold start handling?

### 3. High-Level Design
- Event ingestion from clients (plays, clicks, searches) via Kafka.
- Stream processing to build near-real-time features.
- Batch processing for long-horizon aggregates.
- Feature store with online + offline stores.
- Model training pipeline and model registry.
- Low-latency retrieval/ranking service.

### 4. Detailed Design
**Architecture (text diagram)**

```text
Clients -> API Gateway -> Kafka -> Stream Processor (Spark/Flink)
                                  -> Real-time Feature Store (Redis/Cassandra)

Raw Events -> Data Lake (S3/ADLS) -> Batch ETL (Spark) -> Offline Feature Store (Parquet/Delta)
                                                     -> Training Dataset -> Model Training (ML platform)
                                                     -> Model Registry -> Model Serving

Recommendation Service -> Online Feature Store + Model -> Top-N response
```

Data layers:
- Bronze: raw immutable events.
- Silver: cleaned/deduped/sessionized.
- Gold: user-content features (recency, watch-time embeddings, CTR stats).

### 5. Trade-offs
- Flink for lower latency vs Spark for ecosystem familiarity.
- Redis online store speed vs cost at scale.
- Strong feature parity increases complexity but improves model consistency.

### 6. Scaling Strategy
- Kafka partitioning by user_id.
- Stream processor autoscaling by lag.
- Feature table partitioning by date/user hash.
- Candidate retrieval pre-computation to reduce online compute.

### 7. Failure Handling
- DLQ for malformed events.
- Exactly-once-ish via checkpoints + idempotent upserts.
- Backfill from lake raw logs.
- Alerts on feature freshness, pipeline lag, serving p99 latency.

---

## 2) Design Uber Surge Pricing Data System

### 1. Problem Statement
Design real-time surge pricing pipeline using demand/supply signals with low latency.

### 2. Clarifying Questions
- SLA for surge update? (e.g., every 30s)
- Granularity? (geo-hash tiles)
- Regulatory guardrails/caps?
- Rollback requirements for bad surge updates?

### 3. High-Level Design
- Ingest ride requests, driver availability, trip starts/completions.
- Stream aggregation per geo/time window.
- Compute demand/supply ratio and surge multiplier.
- Publish surge updates to pricing service + analytics store.

### 4. Detailed Design
```text
Rider/Driver Apps -> Kafka topics (requests, pings, trips)
                   -> Stream Engine (Flink/Spark Streaming)
                      -> Windowed Aggregations (geo_hash, 1-min sliding)
                      -> Surge Calculator (rules + ML)
                      -> Redis (current surge by geo)
                      -> Pricing API reads Redis

All events -> Lakehouse -> Batch calibration + model retraining
```

Core metrics:
- Active requests per geo
- Available drivers per geo
- ETA and cancel rate feedback loops

### 5. Trade-offs
- Smaller geo buckets improve precision but increase noise.
- More frequent updates reduce lag but increase jitter and user confusion.
- Rule-based safer; ML-based potentially more optimal but harder to govern.

### 6. Scaling Strategy
- Partition streams by geo_hash.
- State store sharding.
- Hotspot mitigation for downtown geos.
- Tiered compute for peak events.

### 7. Failure Handling
- Fallback to last known safe surge.
- Circuit breaker when input metrics stale.
- Audit logs for all multiplier changes.
- Canary rollout by city.

---

## 3) Design Log Analytics Platform

### 1. Problem Statement
Build a high-ingestion log analytics platform for product + infra logs with fast query.

### 2. Clarifying Questions
- Ingestion rate (TB/day)?
- Query SLA (sub-second vs seconds)?
- Retention tiers (hot/warm/cold)?
- Full-text search required?

### 3. High-Level Design
- Agents ship logs to ingestion bus.
- Parse/enrich/index pipeline.
- Store hot indexed data + cold archival.
- Query API and dashboard integration.

### 4. Detailed Design
```text
App/Infra -> FluentBit/Vector -> Kafka
          -> Stream Parse/Enrich (Flink/Spark)
             -> Hot Store (OpenSearch/ClickHouse)
             -> Lakehouse Archive (S3 + Delta/Iceberg)

Query UI/API -> Search Cluster (hot)
            -> Federated query to lake for long-range analytics
```

Enrichment:
- service metadata, env, version
- trace_id/session_id correlation

### 5. Trade-offs
- OpenSearch flexible search vs ClickHouse analytics speed.
- High-cardinality fields improve debug ability but increase index cost.
- Sampling reduces cost but may miss rare incidents.

### 6. Scaling Strategy
- Topic partitioning by service/env.
- Index lifecycle policies (hot→warm→cold).
- Pre-aggregated materialized views for common dashboards.

### 7. Failure Handling
- Backpressure controls at ingestion.
- Retry with exponential backoff.
- DLQ for parser failures.
- Replica shards and cross-AZ deployments.

---

## 4) Design E-commerce Unified Data Pipeline (Orders, Customers, Payments)

### 1. Problem Statement
Design a robust data platform integrating orders/customers/payments for BI + ML use cases.

### 2. Clarifying Questions
- Freshness for BI dashboards? (hourly?)
- Need real-time fraud/ops alerts?
- Source systems: OLTP DB + payment gateway + CRM?
- SCD requirements for customer profile changes?

### 3. High-Level Design
- CDC ingestion from OLTP.
- Stream + batch transformations.
- Curated warehouse marts for analytics.
- Data quality and reconciliation framework.

### 4. Detailed Design
```text
OLTP DB (orders/customers) --CDC--> Kafka --> Bronze Delta
Payment Gateway API -----------------------> Bronze Delta

Bronze -> Silver (dedup, standardize, late data handling)
Silver -> Gold marts:
  - fact_orders
  - dim_customers (SCD2)
  - fact_payments
  - order_payment_reconciliation

Gold -> BI (Looker/PowerBI), ML feature pipelines
```

Data quality:
- Non-null keys, referential checks, amount reconciliation.
- SLA monitors on freshness and row count drift.

### 5. Trade-offs
- CDC low latency vs higher operational complexity.
- Denormalized marts faster BI, slower updates.
- Strong validation increases reliability but adds pipeline latency.

### 6. Scaling Strategy
- Partition by event_date/order_date.
- Incremental merges.
- Compute autoscaling and workload isolation.

### 7. Failure Handling
- Checkpointed ingestion + replay.
- Idempotent merge logic.
- Quarantine invalid records.
- Reconciliation reports and automatic alerts.

---

## 5) Design Real-Time Fraud Detection Data Platform

### 1. Problem Statement
Detect and score potentially fraudulent transactions in near real time.

### 2. Clarifying Questions
- Decision latency target (<100ms / <1s)?
- False positive tolerance?
- Rules only or ML + rules hybrid?
- Explainability/audit requirements?

### 3. High-Level Design
- Streaming ingestion of payment/fraud signals.
- Feature computation (velocity, geo mismatch, device reputation).
- Online scoring service.
- Feedback loop for labels and model retraining.

### 4. Detailed Design
```text
Payments + Events -> Kafka -> Stream Features (Flink/Spark)
                           -> Online Feature Store (Redis/Cassandra)
Transaction API -> Scoring Service (Rules + Model)
                -> Decision (allow/challenge/block)
                -> Decision Log topic -> Lakehouse

Lakehouse -> Label join (chargebacks) -> Training pipeline -> Model registry -> Deploy
```

### 5. Trade-offs
- Lower latency may reduce feature richness.
- Strict blocking reduces fraud but increases customer friction.
- Complex ML boosts recall but harder to explain to compliance.

### 6. Scaling Strategy
- Partition by card_id/user_id.
- Stateful stream scaling with checkpointed state.
- Hot key mitigation for high-frequency merchants/cards.

### 7. Failure Handling
- Fallback to rule-only mode if model service unavailable.
- Store-and-forward when sink down.
- Exactly-once-ish processing with idempotent event IDs.
- Comprehensive audit trail for every decision.

---

## 6) Design CDC Platform for Multi-Region Databases

### 1. Problem Statement
Replicate multi-region OLTP changes to lakehouse with ordering guarantees.

### 2. Clarifying Questions
- Cross-region consistency requirements?
- Conflict resolution strategy?
- Expected throughput per region?

### 3. High-Level Design
Debezium/Kafka Connect per region, central event bus, ordering/reconciliation layer, lakehouse sinks.

### 4. Detailed Design
- Topic naming by region/table.
- Envelope metadata with source LSN, op type, tx id.
- Merge logic based on source timestamp + version.

### 5. Trade-offs
Global ordering expensive; per-key ordering practical.

### 6. Scaling Strategy
Shard by table/key, independent consumers per domain.

### 7. Failure Handling
Offset checkpointing, replay from Kafka, poison message DLQ.

---

## 7) Design Feature Store for Batch + Streaming Features

### 1. Problem Statement
Unified feature platform for online inference and offline training parity.

### 2. Clarifying Questions
- Online latency target?
- Max feature staleness allowed?
- Number of models/teams?

### 3. High-Level Design
Ingest features from stream + batch, registry, online key-value store, offline parquet store.

### 4. Detailed Design
- Feature definitions as code.
- Point-in-time correct joins for training.
- Online TTL and freshness metrics.

### 5. Trade-offs
Strong parity adds complexity but reduces training-serving skew.

### 6. Scaling Strategy
Entity key sharding, caching, feature group isolation.

### 7. Failure Handling
Backfill pipelines, stale-feature fallback, version rollback.

---

## 8) Design Data Quality Monitoring Platform

### 1. Problem Statement
Centralized quality checks and alerts for critical data assets.

### 2. Clarifying Questions
- Scope: schema, freshness, distribution, business rules?
- Alert channels and severity?
- Auto-remediation needed?

### 3. High-Level Design
Metadata catalog + rules engine + scheduler + incident dashboard.

### 4. Detailed Design
- Rule configs per table/column.
- Daily/stream checks.
- SLA breach alerting and ticket creation.

### 5. Trade-offs
Too many checks can raise noise and compute cost.

### 6. Scaling Strategy
Prioritize critical datasets, tiered check frequency.

### 7. Failure Handling
Retry checks, suppress flapping alerts, runbook links.

---

## 9) Design Real-Time Clickstream Analytics

### 1. Problem Statement
Compute real-time user behavior metrics for product dashboards.

### 2. Clarifying Questions
- Dashboard latency (<1 min)?
- Cardinality of dimensions?
- Sessionization rules?

### 3. High-Level Design
Kafka ingestion -> stream aggregation -> serving DB + lake archival.

### 4. Detailed Design
- Windowed metrics: DAU, funnel steps, session duration.
- Late event handling with watermark.
- Serving via Druid/ClickHouse.

### 5. Trade-offs
Low latency may sacrifice late-event completeness.

### 6. Scaling Strategy
Partition by user/session key, autoscale consumers.

### 7. Failure Handling
Checkpointing, replay from offsets, DLQ for malformed events.

---

## 10) Design Unified Metrics Layer for BI

### 1. Problem Statement
Create consistent metric definitions across teams.

### 2. Clarifying Questions
- Which KPIs conflict currently?
- Need semantic layer?
- Governance owner?

### 3. High-Level Design
Semantic model on top of curated marts with governed definitions.

### 4. Detailed Design
- Metric contracts (SQL + owner + tests).
- Versioned changes and approvals.
- Dashboard integration.

### 5. Trade-offs
Strong governance slows ad-hoc speed but improves trust.

### 6. Scaling Strategy
Domain ownership + central standards.

### 7. Failure Handling
Version rollback and metric discrepancy alerts.

---

## 11) Design Batch + Streaming Lambda Architecture

### 1. Problem Statement
Need both low-latency and accurate historical recomputation.

### 2. Clarifying Questions
- Is Kappa viable instead?
- How much duplication acceptable?

### 3. High-Level Design
Speed layer (stream), batch layer (recompute), serving layer merge.

### 4. Detailed Design
- Stream produces provisional metrics.
- Batch recalculates truth.
- Serving reconciles final values.

### 5. Trade-offs
Operationally heavy due to dual pipelines.

### 6. Scaling Strategy
Separate compute pools for speed/batch layers.

### 7. Failure Handling
Fallback to batch truth when stream degraded.

---

## 12) Design GDPR/PII Deletion Pipeline

### 1. Problem Statement
Propagate right-to-be-forgotten deletions across lake/warehouse/indices.

### 2. Clarifying Questions
- SLA for deletion completion?
- Immutable logs exceptions?

### 3. High-Level Design
Deletion request bus + policy engine + downstream deletion workers.

### 4. Detailed Design
- Identity mapping service.
- Delete/tombstone propagation.
- Compliance audit trail.

### 5. Trade-offs
Hard deletes expensive; soft deletes may violate policy.

### 6. Scaling Strategy
Batch delete windows + prioritized queue.

### 7. Failure Handling
Retry with idempotent delete events and compliance alerts.

---

## 13) Design Backfill Framework

### 1. Problem Statement
Run safe large-scale historical reprocessing without breaking production SLAs.

### 2. Clarifying Questions
- Backfill window size?
- Can production tables be overwritten?

### 3. High-Level Design
Parameterized reprocessing engine with isolated compute and validation gates.

### 4. Detailed Design
- Run IDs and manifests.
- Shadow tables then swap.
- Automated reconciliation checks.

### 5. Trade-offs
Shadow writes increase cost but reduce risk.

### 6. Scaling Strategy
Partitioned backfill and throttled concurrency.

### 7. Failure Handling
Checkpoint by partition and resume.

---

## 14) Design Multi-Cloud Data Lake Pipeline

### 1. Problem Statement
Move/process analytics data across AWS/GCP/Azure with governance.

### 2. Clarifying Questions
- Cross-cloud transfer frequency/cost constraints?
- Data residency requirements?

### 3. High-Level Design
Cloud-local ingestion with cross-cloud normalized layer and metadata catalog.

### 4. Detailed Design
- Object storage replication jobs.
- Standardized schema contracts.
- Central orchestration and lineage tracking.

### 5. Trade-offs
Multi-cloud resilience vs heavy operational complexity.

### 6. Scaling Strategy
Regional hubs, compression, incremental transfer.

### 7. Failure Handling
Transfer retries, checksums, reconciliation reports.

---

## 15) Design Cost-Optimized Warehouse Pipeline

### 1. Problem Statement
Reduce warehouse costs while preserving SLA.

### 2. Clarifying Questions
- Biggest current cost drivers?
- SLA flexibility for cold reports?

### 3. High-Level Design
Tiered storage + pre-aggregations + query governance.

### 4. Detailed Design
- Materialized views for hot queries.
- Auto-suspend/scale compute.
- Archival of cold partitions.

### 5. Trade-offs
Aggressive cost cuts may increase query latency.

### 6. Scaling Strategy
Workload management queues by priority.

### 7. Failure Handling
Fallback queries and stale-cache fallback.

---

## 16) Design Real-Time Ride Tracking Data System

### 1. Problem Statement
Track rides in real time for ETA, ops, and analytics.

### 2. Clarifying Questions
- Location ping frequency?
- Required latency for ETA refresh?

### 3. High-Level Design
Streaming GPS ingestion -> map matching -> state store -> APIs + analytics.

### 4. Detailed Design
- Geospatial indexing.
- Out-of-order event correction.
- Real-time and historical stores.

### 5. Trade-offs
Higher ping rate improves precision but increases ingest cost.

### 6. Scaling Strategy
Partition by ride_id/city, hot city autoscaling.

### 7. Failure Handling
Fallback to last known location and stale-data flags.

---

## 17) Design SLA Monitoring System for Pipelines

### 1. Problem Statement
Detect and escalate SLA risks across hundreds of pipelines.

### 2. Clarifying Questions
- Types of SLAs: freshness, completeness, correctness?
- Escalation policy?

### 3. High-Level Design
Metadata collector + rules engine + alerting + dashboard.

### 4. Detailed Design
- Pipeline heartbeat events.
- Expected vs actual completion windows.
- Burn-rate style alerts.

### 5. Trade-offs
Strict thresholds increase false positives.

### 6. Scaling Strategy
Domain-level ownership and templated rules.

### 7. Failure Handling
Retry windows and incident auto-ticketing.

---

## 18) Design Self-Service Data Platform

### 1. Problem Statement
Enable teams to publish trusted datasets without centralized bottleneck.

### 2. Clarifying Questions
- User persona: analysts, DS, engineers?
- Required governance guardrails?

### 3. High-Level Design
Portal for dataset registration, schema contracts, quality checks, lineage.

### 4. Detailed Design
- Dataset SDK/templates.
- CI data tests.
- Access control and approvals.

### 5. Trade-offs
Self-service speed vs governance control.

### 6. Scaling Strategy
Standardized blueprints and domain stewards.

### 7. Failure Handling
Automated rollback and deprecation flow.

---

## 19) Design Recommendation Batch Retraining Pipeline

### 1. Problem Statement
Daily retraining with feature drift detection and safe rollout.

### 2. Clarifying Questions
- Retrain frequency?
- Offline/online metric thresholds?

### 3. High-Level Design
Feature snapshot -> training -> evaluation -> canary deployment.

### 4. Detailed Design
- Data/feature versioning.
- Champion/challenger framework.
- Rollback automation.

### 5. Trade-offs
More validations improve safety, increase cycle time.

### 6. Scaling Strategy
Distributed training and cached feature reuse.

### 7. Failure Handling
Freeze to previous model and incident notification.

---

## 20) Design Payment Reconciliation Platform

### 1. Problem Statement
Reconcile internal order payments with external processor reports.

### 2. Clarifying Questions
- T+0 or T+1 reconciliation?
- Tolerance for timing mismatch?

### 3. High-Level Design
Dual-ingest + normalization + matching engine + exception workflow.

### 4. Detailed Design
- Match on order_id, amount, currency, time window.
- Exception buckets and auto-retry.
- Finance reporting layer.

### 5. Trade-offs
Strict matching reduces false negatives but may increase exception queue.

### 6. Scaling Strategy
Incremental matching and partitioned workloads.

### 7. Failure Handling
Replay support and immutable audit logs.

---

## 21) to 50) Additional System Design Prompts (Use same 7-part structure in interviews)
To keep this repository practical and reviewable, use the above canonical answer format for these additional high-frequency interview prompts:
21. Data lineage platform
22. Real-time KPI dashboard backend
23. Inventory forecasting pipeline
24. Ads attribution data platform
25. Search ranking feature pipeline
26. IoT telemetry ingestion system
27. Multi-tenant analytics platform
28. Streaming anomaly detection
29. Event schema registry platform
30. ML feature backfill system
31. User 360 profile pipeline
32. Data contract enforcement platform
33. Data access governance system
34. High-cardinality metrics store
35. Nearline personalization pipeline
36. Graph feature pipeline
37. Fraud rules engine data backend
38. Batch orchestration platform redesign
39. Lakehouse migration strategy
40. CDC to warehouse sync service
41. Data retention and tiering platform
42. Metadata catalog and discovery
43. Real-time geospatial analytics
44. In-app experiment analytics platform
45. Recommendation feedback loop platform
46. Search clickstream ETL design
47. Streaming dedup service
48. Warehouse workload isolation design
49. Event replay and backfill framework
50. Unified observability data pipeline

> Interview prep tip: For each of the 21–50 prompts, practice delivering the **same 7-section structure** in under 10 minutes with one diagram, two trade-offs, and one failure scenario.
