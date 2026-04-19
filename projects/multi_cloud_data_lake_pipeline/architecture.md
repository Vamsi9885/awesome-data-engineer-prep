# Architecture — Multi-Cloud Data Lake Pipeline

## High-Level Architecture Diagram (Text)

```text
                        ┌───────────────────────────────────────────┐
                        │        Global Control Plane               │
                        │  Orchestrator (Airflow/ADF/Composer)      │
                        │  Metadata Catalog + Data Contracts         │
                        └───────────────┬───────────────────────────┘
                                        │
           ┌────────────────────────────┼─────────────────────────────┐
           │                            │                             │
┌──────────▼──────────┐       ┌─────────▼─────────┐        ┌─────────▼─────────┐
│ AWS Region          │       │ Azure Region      │        │ GCP Region         │
│ S3 Raw Landing      │       │ ADLS Raw Landing  │        │ GCS Raw Landing    │
│ Orders, Clickstream │       │ Payments, Catalog │        │ Returns, Sessions  │
└──────────┬──────────┘       └─────────┬─────────┘        └─────────┬─────────┘
           │                            │                             │
           └──────────────┬─────────────┴──────────────┬──────────────┘
                          │    Federated Ingestion     │
                          │  (Autoloader + CDC + API)  │
                    ┌─────▼─────────────────────────────▼─────┐
                    │      Databricks Lakehouse (Spark)        │
                    │ Bronze (immutable)                        │
                    │ Silver (validated + canonical schema)     │
                    │ Gold (serving marts / features)           │
                    │ Delta Lake + Unity Catalog + DQ checks    │
                    └─────┬─────────────────────────────┬───────┘
                          │                             │
              ┌───────────▼───────────┐     ┌──────────▼────────────┐
              │ Snowflake Global Mart │     │ BigQuery APAC Mart    │
              │ BI + Finance + Ops    │     │ DS + Product Analytics│
              └───────────┬───────────┘     └──────────┬────────────┘
                          │                             │
                     ┌────▼─────────────────────────────▼────┐
                     │ Dashboards / Experiments / APIs        │
                     │ (Looker, Power BI, Internal Services)  │
                     └─────────────────────────────────────────┘
```

---

## Service Mapping by Cloud

### AWS
- S3: regional raw landing
- Glue Data Catalog (optional interoperability)
- IAM + KMS for identity/encryption
- CloudWatch for ingestion observability

### Azure
- ADLS Gen2: regional raw landing + curated zone
- Azure Key Vault + Managed Identity for secrets/access
- Azure Monitor for pipeline telemetry

### GCP
- Cloud Storage: regional raw landing
- BigQuery: low-latency serving and ad-hoc analytics
- Cloud Logging for operational metrics

### Common Processing Layer
- Databricks on multi-cloud workspaces
- Delta Lake for ACID upserts and schema evolution
- Unity Catalog for governance and access policies

---

## Why This Architecture

1. **Federated raw + centralized canonical processing**  
   Keeps data residency boundaries while enabling global analytics through standardized silver/gold layers.

2. **Delta-based medallion model**  
   Enables idempotent merges, time travel, reliable backfills, and deterministic replay.

3. **Dual serving stores (Snowflake + BigQuery)**  
   Supports enterprise BI and regional analytics needs with minimal data movement from raw zones.

4. **Contract-first schema governance**  
   Prevents downstream breakage from independent regional team changes.

---

## Data Flow and Reliability Strategy

1. Regional landing buckets receive immutable raw files/events.
2. Ingestion jobs write bronze with ingest metadata:
   - `ingest_ts`, `source_cloud`, `source_file`, `event_id`, `batch_id`
3. Silver applies:
   - schema standardization
   - dedupe via business key + event timestamp + hash
   - quarantine bad records
4. Gold aggregates and dimensional models.
5. Serving exports run with checkpointed incremental logic.

Reliability mechanisms:
- exactly-once behavior via Delta `MERGE` + deterministic keys
- checkpointing for streaming/autoloader
- dead-letter paths for malformed records
- retries with exponential backoff and run-id isolation

---

## Partitioning and File Strategy

- Bronze: partition by `ingest_date`, `source_cloud`
- Silver:
  - orders/payments by `event_date`, `region`
  - clickstream by `event_date`, `hour`
- Gold:
  - business marts by `ds` (daily snapshot date)

Performance controls:
- optimize writes to target 128–512 MB files
- scheduled compaction + vacuum policy
- Z-ORDER on high-selectivity columns (`customer_id`, `country`, `order_id`)

---

## Real-World Failure Scenarios and Recovery

1. **One cloud delayed (e.g., Azure outage)**  
   - proceed with partial refresh mark + freshness status
   - replay missed partitions using run bookmarks
2. **Schema breaking change in partner feed**  
   - contract validation fails
   - route to quarantine and alert on-call
3. **Duplicate surges from replayed files**  
   - dedupe with deterministic hash key and watermark windows
4. **Skewed partition causing long stage time**  
   - adaptive execution + salting + pre-aggregation to reduce shuffle skew

---

## Security and Governance

- column-level masking for PII in silver/gold
- row-level access by region and domain
- immutable audit trail of each job run + data quality score
- lineage from source object -> target table for incident triage

---

## Cost and Scaling Trade-offs

- **Spark vs Dataflow**: Spark chosen for unified batch/streaming and Delta-native ACID semantics.
- **Delta vs Parquet-only**: Delta chosen for update/delete/merge reliability; Parquet-only cheaper but operationally fragile.
- **Centralized compute vs per-cloud compute**:
  - centralized gives consistency and easier governance
  - per-cloud reduces egress but increases operational complexity

---

## Interview Prompts (Architecture Focus)

1. If cross-cloud network latency increases 3x, what changes in ingestion and serving?
2. Which components are single points of failure and how are they mitigated?
3. How do you prove consistency between Snowflake and BigQuery business metrics?
4. How does this design evolve for near-real-time recommendations?
