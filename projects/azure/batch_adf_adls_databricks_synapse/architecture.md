# Architecture — Azure End-to-End Batch Pipeline (ADF + ADLS + Databricks + Synapse)

## 1) Text-Based Architecture Diagram

```text
                    +---------------------------+
                    |     Source Systems        |
                    |---------------------------|
                    | Azure SQL (orders/payments/customers)
                    | Partner REST API (refunds)
                    | Blob CSV drops (inventory)
                    +-------------+-------------+
                                  |
                                  v
                    +---------------------------+
                    | Azure Data Factory (ADF)  |
                    |---------------------------|
                    | Copy pipelines + metadata |
                    | dynamic partition windows |
                    | retries + alerts          |
                    +-------------+-------------+
                                  |
                                  v
                    +---------------------------+
                    | ADLS Gen2 - Raw Zone      |
                    | /raw/{source}/{dt}/       |
                    | immutable + versioned      |
                    +-------------+-------------+
                                  |
                                  v
                    +---------------------------+
                    | Azure Databricks + Delta  |
                    |---------------------------|
                    | Bronze (normalize, dedup) |
                    | Silver (quality, business)|
                    | Gold (facts/dims, SCD2)   |
                    +-------------+-------------+
                                  |
                    +-------------+-------------+
                    |                           |
                    v                           v
        +------------------------+   +-------------------------+
        | Synapse Dedicated SQL  |   | Monitoring & Ops        |
        |------------------------|   |-------------------------|
        | fact_orders            |   | ADF Monitor, Log Analytics
        | fact_payments          |   | Azure Monitor Alerts    |
        | dim_customer (SCD2)    |   | Data quality metrics    |
        | dim_product            |   | lineage + reconciliation|
        +------------------------+   +-------------------------+
```

---

## 2) Service Justification

- **Azure Data Factory (ADF)**  
  Best fit for scheduled enterprise ingestion, dependency orchestration, copy activities, and managed retries with minimal custom code.

- **ADLS Gen2**  
  Durable, low-cost lake storage with hierarchical namespace and strong integration across ADF, Databricks, and Synapse.

- **Azure Databricks + Delta Lake**  
  Required for scalable transformation, robust MERGE-based idempotency, SCD2 handling, schema evolution controls, and performant partition processing.

- **Azure Synapse Dedicated SQL Pool**  
  Serves BI-ready dimensional model with predictable query performance for morning dashboards.

- **Azure Monitor + Log Analytics**  
  Centralized observability (SLA tracking, failures, lag, and cost anomalies).

---

## 3) End-to-End Reliability Strategy

1. **Ingestion contracts** with schema and watermark metadata per source.
2. **Immutable raw writes** to ADLS with ingestion timestamp and run_id.
3. **Bronze deduplication** by business keys + update timestamp.
4. **Silver validations** (null/range/referential checks) and quarantine path.
5. **Gold deterministic MERGE** (idempotent reruns and backfill-safe).
6. **Synapse load via staged partitions**, then atomic table swap.
7. **Reconciliation checks** for row counts and financial totals.
8. **Alerting and retry policies** at ADF and Databricks task level.

---

## 4) Real-World Challenge Handling

- **Skew:** country-based skew mitigated via salting + adaptive execution.
- **Late data:** rolling correction window (N days) with controlled MERGE refresh.
- **Duplicates:** deterministic dedup keys in bronze and idempotent MERGE in gold.
- **Schema evolution:** add-only default policy, schema registry metadata, compatibility checks.
- **Backfill:** parameterized date-range reprocessing with partition-level reruns.

---

## 5) Performance and Cost Scaling

- Partition strategy:
  - Raw/Bronze: `ingest_date`
  - Silver/Gold facts: `business_date`, `country`
- Delta optimizations:
  - OPTIMIZE + ZORDER on high-filter columns.
  - Auto compaction and small-file mitigation.
- Autoscaling:
  - Databricks jobs cluster autoscaling based on load.
  - Synapse workload isolation for dashboard SLA.
- Cost controls:
  - Stop/start Synapse pool outside serving window.
  - Spot/low-priority nodes where feasible for non-critical backfills.

---

## 6) Failure Recovery & Idempotency

- ADF activity retries with exponential backoff.
- Databricks task retries with checkpointed progress.
- Partition-level restart support (no full rerun required).
- Delta transaction log guarantees atomicity and replay safety.
- Recovery target:
  - failed partition rerun under 60 minutes (RTO objective).

---

## 7) Interview Questions

1. Why choose ADF + Databricks over all-in-Synapse pipelines?
2. How is exactly-once behavior approximated in this batch architecture?
3. What is your strategy for quarter-over-quarter schema drift from partner APIs?
4. How do you keep costs bounded while preserving 6:30 AM SLA?
5. How do you validate financial correctness after reruns/backfills?
