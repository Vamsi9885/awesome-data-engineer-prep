# 📏 Normalization vs Denormalization

## 1) Concept Explanation

Normalization and denormalization solve different problems.

- **Normalization (3NF/BCNF)**: reduce redundancy, protect integrity, optimized for transactions
- **Denormalization (star-like)**: duplicate selected attributes for read speed, optimized for analytics

Interview framing:
- OLTP favors normalized design
- OLAP favors denormalized dimensional design
- Mature platforms often use both: source OLTP + warehouse marts

---

## 2) Text-Based Diagrams

### 2.1 Normalized OLTP (3NF)

```text
customers ----< orders ----< order_items >---- products ---- categories
```

### 2.2 Denormalized Analytics

```text
fact_order_line
---------------
order_line_id
order_id
customer_key
product_key
date_key
customer_city         (sometimes kept in dim only)
product_category
quantity
line_amount

dim_customer, dim_product, dim_date
```

---

## 3) Real-World Use Case

### Amazon ecosystem
- Order placement service uses normalized transactional schema for consistency.
- Analytics warehouse uses star/denormalized marts for dashboards:
  - conversion
  - AOV
  - repeat rate
  - Prime behavior cohorts

### Uber
- Trip lifecycle OLTP tables normalized.
- Marketplace and growth dashboards use curated denormalized marts.

### Netflix
- Operational metadata normalized in source services.
- Engagement analytics modeled for fast aggregate exploration.

---

## 4) When to Use / When NOT to Use

### Normalize when
- Transaction integrity is critical
- High write/update workloads
- Need strict constraints and minimal anomalies

### Denormalize when
- Read-heavy analytical workloads
- BI/reporting and ad-hoc analysis
- Query simplicity/performance is primary

### Avoid
- Over-normalizing warehouse marts
- Blind denormalization in write-heavy systems

---

## 5) Advantages & Disadvantages

## Normalization
### Advantages
- Strong data integrity
- Less redundancy
- Easier update correctness

### Disadvantages
- Many joins for analytics
- Slower complex read queries
- Harder for business users

## Denormalization
### Advantages
- Faster analytical queries
- Simpler SQL for BI users
- Better dashboard responsiveness

### Disadvantages
- Redundancy/storage overhead
- Update complexity
- Risk of inconsistency if pipeline quality is weak

---

## 6) Common Mistakes

1. Applying OLTP 3NF model directly to BI layer
2. Duplicating too many columns without lineage ownership
3. No governance of denormalized attribute refresh logic
4. Ignoring grain when flattening data
5. Treating normalization/denormalization as ideological instead of workload-based

---

## 7) Performance Considerations

- For OLTP: proper indexing + normalized writes
- For OLAP: partition/cluster fact tables, prune columns, denormalized dimensions
- Use materialized views for repetitive heavy KPIs
- Profile join count and scanned bytes regularly
- Maintain semantic layer with tested business definitions

---

## 8) 🔥 Interview Questions

### Conceptual
1. Why is denormalization common in data warehouses?
2. 3NF vs star schema: core trade-offs?
3. When would BCNF matter in data engineering?

### Scenario-based
1. Dashboard latency is 25s on normalized warehouse tables. What redesign do you propose?
2. Denormalized mart has inconsistent product category labels. How do you fix architecture?
3. You must support both real-time order writes and hourly BI dashboards. Model strategy?

### Product-based
1. Design OLTP + OLAP modeling split for Amazon orders.
2. Uber trip booking schema in 3NF; convert for analytics marts.
3. Netflix content metadata normalization vs watch analytics denormalization.

### Follow-ups
- How do you keep denormalized models trustworthy?
- What metrics show you denormalization is needed?
- How do you phase migration from normalized reports to star marts?
