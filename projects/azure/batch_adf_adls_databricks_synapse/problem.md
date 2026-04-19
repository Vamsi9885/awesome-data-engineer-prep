# Problem Statement — Azure End-to-End Batch Pipeline

## Business Problem

An e-commerce company running in 12 countries needs a **daily financial and operations data pipeline**. Source systems (Azure SQL + partner APIs + CSV drops) produce orders, payments, refunds, and inventory snapshots. Leadership needs curated dashboards by 7:00 AM UTC.

Current pain points:
- delayed daily reporting (manual extracts)
- duplicates from retrying ingestion jobs
- no replay strategy when source outages happen
- poor partitioning causing high Databricks and Synapse costs

---

## Requirements

## Functional
1. Ingest daily incremental data from:
   - Azure SQL (`orders`, `payments`, `customers`)
   - Blob CSV snapshots (`inventory`)
   - REST partner API (`refunds`)
2. Store immutable raw data in ADLS.
3. Transform to bronze/silver/gold using Databricks + Delta Lake.
4. Publish dimensional model into Synapse:
   - `fact_orders`
   - `fact_payments`
   - `dim_customer` (SCD2)
   - `dim_product`
5. Guarantee idempotent re-runs for any date range.
6. Support backfill for at least 24 months.

## Non-Functional
- Data freshness SLA: Gold layer ready by 06:30 AM UTC
- Availability: 99.9% successful daily run rate
- Recovery Time Objective (RTO): < 60 minutes for failed partition rerun
- Cost guardrail: keep Databricks DBU and Synapse DWU within monthly budget
- Security: Managed Identity + Key Vault secrets + RBAC

---

## Data Volumes & Constraints

- Orders: ~80M/day peak
- Payments: ~90M/day peak
- Inventory snapshots: 2.5 TB/day compressed
- Source skew on large marketplaces (top 2 countries = 50% volume)
- Schema changes from partner API every quarter

---

## Success Criteria

1. Daily run completes before SLA for 95th percentile days.
2. Duplicate rate in gold tables < 0.01%.
3. Data reconciliation variance vs source < 0.05%.
4. Backfill for one month completes in under 4 hours.
5. Interview readiness:
   - explain idempotency strategy
   - explain late data correction
   - explain exactly-once outcomes with Delta MERGE
   - explain fault tolerance and monitoring model

---

## Interview Questions (Project-Specific)

1. How will you scale this pipeline during holiday traffic spikes?
2. How do you handle source schema drift without downtime?
3. How do you optimize cost between ADF copy, Databricks compute, and Synapse?
4. What are trade-offs of loading Synapse directly vs serving from Delta?
