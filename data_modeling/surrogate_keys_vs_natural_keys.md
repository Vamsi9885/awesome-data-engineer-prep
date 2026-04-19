# 🗝️ Surrogate Keys vs Natural Keys

## 1) Concept Explanation

A key identifies a row uniquely.

- **Natural key**: comes from business domain (customer_id, email, driver_license_no)
- **Surrogate key**: system-generated stable identifier (integer/bigint UUID)

Interview framing for warehouses:
- Use natural keys for business identity tracking
- Use surrogate keys for dimensional joins and SCD handling

---

## 2) Text-Based Diagrams

```text
dim_customer
------------
customer_key      (surrogate PK)
customer_id       (natural business id)
customer_name
city
effective_date
end_date
is_current
```

```text
fact_order_line
---------------
order_line_id
customer_key   (FK to dim_customer surrogate key)
product_key
date_key
line_amount
```

Why not natural key in facts for SCD2?

```text
customer_id=123 can map to multiple historical rows in dim_customer
customer_key is unique per version row -> correct point-in-time joins
```

---

## 3) Real-World Use Case

### Amazon customer SCD2
- Natural key: `customer_id` from operational systems
- Surrogate key: `customer_key` generated in warehouse for each SCD2 version row

Fact rows reference `customer_key` to keep historical context stable.

### Uber
Driver natural id can originate from multiple systems; surrogate key unifies warehouse identity per SCD version.

---

## 4) When to Use / When NOT to Use

### Use surrogate keys when
- Building dimensional models
- Handling SCD Type 2
- Integrating multiple source systems with conflicting IDs

### Keep natural keys when
- Data quality reconciliation with source systems
- Business-level dedupe and identity matching
- Operational APIs referencing domain IDs

### Avoid
- Using mutable natural keys as warehouse fact FKs
- Surrogate-only models without natural key lineage column

---

## 5) Advantages & Disadvantages

## Surrogate keys
### Advantages
- Stable and compact joins
- Decouples warehouse from source key volatility
- Enables multiple history rows per natural key (SCD2)

### Disadvantages
- Extra ETL step (key lookup/generation)
- Requires strict key management
- Harder debugging without retained natural keys

## Natural keys
### Advantages
- Business meaningful
- Useful for source traceability and reconciliation

### Disadvantages
- Can change, collide, be reused, or be non-global
- Larger string joins are slower
- Not sufficient alone for SCD2 history rows

---

## 6) Common Mistakes

1. Fact tables joining to natural keys directly
2. Not storing natural key in dimensions (losing lineage)
3. Surrogate key regeneration instability across reloads
4. Using UUID strings in huge fact joins without considering cost
5. No “unknown” surrogate key (-1) handling for missing dimensions

---

## 7) Performance Considerations

- Prefer integer/bigint surrogate keys for joins
- Maintain efficient key lookup tables during ETL
- Cache/broadcast small dimensions in Spark pipelines
- Add unique constraints where engine supports it:
  - natural_key + effective_date (or version)
- Keep unknown/default members for load continuity

---

## 8) 🔥 Interview Questions

### Conceptual
1. Why are surrogate keys preferred in data warehouses?
2. Can natural keys ever be sufficient in dimensions?
3. How do surrogate keys interact with SCD Type 2?

### Scenario-based
1. Customer email (natural key candidate) changes often. What key strategy?
2. Two source systems use overlapping customer_id ranges. How do you model?
3. Reprocessing pipeline changed surrogate IDs and broke dashboards. Root causes/fix?

### Product-based
1. Design Amazon customer/product key strategy for cross-marketplace integration.
2. Uber rider identity unification across mobility and eats systems.
3. Netflix account/profile/entity keys for watch analytics.

### Follow-ups
- How do you generate surrogate keys in distributed pipelines?
- Sequence vs UUID vs hash key trade-offs?
- How do you handle unknown/missing key at load time?
