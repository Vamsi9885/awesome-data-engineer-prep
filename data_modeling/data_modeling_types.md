# 🧱 Data Modeling Types

## 1) Concept Explanation

Different systems require different modeling styles.  
There is no single “best” model; the right model depends on workload, latency, governance, and consumer type.

Key interview-relevant modeling types:
1. OLTP modeling (normalized, transactional)
2. OLAP/dimensional modeling (star/snowflake)
3. Data Vault (raw + business vault + marts)
4. Lakehouse modeling (bronze/silver/gold, medallion, table formats)

---

## 2) Text-Based Diagrams

### 2.1 OLTP (3NF)

```text
customers -> orders -> order_items -> products
```

### 2.2 OLAP (Star)

```text
dim_customer   dim_product   dim_date
      \            |           /
          ---- fact_sales ----
```

### 2.3 Data Vault (simplified)

```text
HUB_CUSTOMER --- LINK_ORDER_CUSTOMER --- HUB_ORDER
      |                                  |
 SAT_CUSTOMER_ATTR                  SAT_ORDER_ATTR
```

### 2.4 Lakehouse Medallion

```text
Bronze (raw) -> Silver (cleaned/conformed) -> Gold (business marts)
```

---

## 3) Real-World Use Case

### Amazon/Uber/Netflix combined pattern
- OLTP model in application DB for writes
- Data Vault or bronze/silver for enterprise ingestion/history
- Gold/star marts for business analytics and experimentation
- Product teams consume gold for KPIs and decisioning

---

## 4) Type-by-Type Guide

## A) OLTP Modeling
- Highly normalized (3NF), constraints, ACID transactions
- Best for order creation, payment capture, trip state transitions

## B) OLAP Modeling
- Fact + dimensions, denormalized for read speed
- Best for BI dashboards, cohort analysis, business metrics

## C) Data Vault (brief)
- Hubs = business keys
- Links = relationships
- Satellites = descriptive history
- Excellent for auditability and schema change tolerance
- Often used as enterprise integration layer before marts

## D) Lakehouse Modeling
- Open table formats (Delta/Iceberg/Hudi), scalable compute
- Medallion architecture:
  - Bronze raw ingestion
  - Silver cleaned + conformed
  - Gold curated dimensional/business models
- Supports batch + streaming convergence

---

## 5) When to Use / When NOT to Use

### OLTP
Use for transactions; avoid for heavy BI.

### OLAP
Use for analytics; avoid for write-intensive app workflows.

### Data Vault
Use for enterprise integration + auditability; avoid if team lacks modeling maturity/time.

### Lakehouse
Use for big data + mixed workloads; avoid if organizationally overkill for tiny static workloads.

---

## 6) Advantages & Disadvantages

## OLTP
+ Integrity, transactional safety  
- Poor analytical ergonomics

## OLAP
+ Fast analytical queries  
- ETL complexity, SCD handling

## Data Vault
+ Auditability, flexibility, historization  
- More tables/complexity, steeper learning curve

## Lakehouse
+ Scale, open formats, unified batch/stream  
- Governance discipline required; cost/perf tuning complexity

---

## 7) Common Mistakes

1. Forcing one model for all workloads
2. Skipping conformance from silver to gold
3. Building marts directly from raw data without contracts
4. Using Data Vault without clear downstream consumption plan
5. Ignoring semantic consistency across product teams

---

## 8) Performance Considerations

- OLTP: indexing + transaction tuning
- OLAP: partition/cluster fact tables, surrogate keys
- Data Vault: optimize PIT (point-in-time) and bridge structures
- Lakehouse: file size compaction, Z-order/clustering, incremental pipelines
- Use cost-aware storage/compute tiering

---

## 9) 🔥 Interview Questions

### Conceptual
1. Compare OLTP, OLAP, Data Vault, and Lakehouse modeling.
2. Why might an enterprise use both Data Vault and star schema?
3. Is Lakehouse a replacement for dimensional modeling?

### Scenario-based
1. You inherit fragmented pipelines from many microservices. Which integration model do you choose and why?
2. Product wants real-time KPIs and historical reproducibility. Which architecture pattern?
3. Team has poor governance and changing schemas weekly. How do you model safely?

### Product-based
1. Design modeling layers for Amazon marketplace analytics.
2. Uber mobility + eats unified analytics: which modeling stack?
3. Netflix content and engagement platform with frequent schema evolution.

### Follow-ups
- Where do SCDs live in this architecture?
- What should be in silver vs gold?
- How do you enforce metric consistency?
