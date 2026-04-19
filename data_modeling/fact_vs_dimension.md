# 📊 Fact vs Dimension

## 1) Concept Explanation

Fact and dimension tables are the foundation of dimensional modeling.

- **Fact table**: stores measurable business events (orders, rides, views)
- **Dimension table**: stores descriptive context (customer, driver, title, date)

Interview framing:
- Fact answers: “how much/how many/what happened?”
- Dimension answers: “for whom/what/when/where/under what attributes?”

---

## 2) Text-Based Diagrams

```text
fact_order_line
---------------
order_line_id
date_key
customer_key
product_key
quantity
line_amount

dim_customer
------------
customer_key
customer_id
customer_name
city
segment

dim_product
-----------
product_key
product_id
product_name
category
brand
```

```text
Join Pattern:
fact_order_line f
JOIN dim_customer c ON f.customer_key = c.customer_key
JOIN dim_product  p ON f.product_key  = p.product_key
```

---

## 3) Real-World Use Case

### Uber trips analytics

Fact: `fact_trip`
- trip_id, rider_key, driver_key, date_key, distance_km, duration_min, fare_amount

Dimensions:
- `dim_rider` (rider attributes)
- `dim_driver` (driver attributes)
- `dim_date` (calendar)
- `dim_city` (geo hierarchy)

Business query:
“Average fare by rider segment and city in peak hours.”

---

## 4) When to Use / When NOT to Use

### Use this pattern when
- Building OLAP warehouse/data marts
- Need slice/dice and KPI aggregation
- Business users need understandable data model

### Avoid direct fact/dimension style when
- Raw event lake zones (bronze)
- High-write OLTP systems
- No curated semantics yet

---

## 5) Advantages & Disadvantages

### Advantages
- Clear separation of events vs context
- Fast analytical queries
- Reusable dimensions across facts
- Easier BI semantic modeling

### Disadvantages
- Requires strict grain discipline
- SCD and surrogate key handling complexity
- ETL quality issues can corrupt joins

---

## 6) Common Mistakes

1. Putting measures in dimensions
2. Putting descriptive text in facts (instead of keys)
3. Missing grain definition in fact table
4. Natural key joins causing instability
5. Not handling late-arriving dimension members
6. Mixing additive and non-additive facts without guidance

---

## 7) Performance Considerations

- Partition fact by date/event time
- Integer surrogate keys for all dim joins
- Keep dimensions reasonably wide but not bloated
- Precompute aggregates for top dashboards
- Ensure join cardinality sanity checks in pipelines

---

## 8) 🔥 Interview Questions

### Conceptual
1. What is the difference between a fact and dimension table?
2. Can a table be both fact and dimension in different contexts?
3. What are additive, semi-additive, and non-additive facts?

### Scenario-based
1. Your fact table has one row per order, but PM needs product-level margin. What do you change?
2. Revenue doubled after joining dim_customer. What could be wrong?
3. How do you model returns/refunds in fact design?

### Product-based
1. Design fact/dimension model for Amazon order funnel.
2. Design ride marketplace model for Uber (request, accept, trip, payment).
3. Design Netflix watch analytics with title and device dimensions.

### Follow-ups
- What is fact table grain?
- How do you handle unknown dimension members?
- When should you split one fact into multiple facts?
