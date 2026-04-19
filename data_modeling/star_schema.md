# ⭐ Star Schema

## 1) Concept Explanation

Star schema is a dimensional modeling pattern optimized for analytics.  
You place **one central fact table** (events/measures) and surround it with **denormalized dimension tables** (context).

Interview framing:
- Think in terms of **business process** first (orders, trips, watches)
- Then define **fact grain** (one row per what?)
- Then attach dimensions that answer who/what/when/where/how

Star schema is popular in product companies because it keeps BI queries simple and predictable at scale.

---

## 2) Text-Based Diagrams

### 2.1 Logical Layout (Star)

```text
                  dim_date
                     |
dim_customer --- fact_order_line --- dim_product
                     |
                 dim_store
                     |
                dim_promotion
```

### 2.2 Example Tables

```text
Fact Table: fact_order_line (grain: one row per order line item)
----------------------------------------------------------------
order_line_id (PK)
order_id
date_key (FK)
customer_key (FK)
product_key (FK)
store_key (FK)
promotion_key (FK)
quantity
unit_price
discount_amount
line_amount

Dimension: dim_customer
-----------------------
customer_key (PK)
customer_id (natural id)
customer_name
city
state
country
customer_tier
signup_date
is_prime

Dimension: dim_product
----------------------
product_key (PK)
product_id
product_name
brand
category
sub_category
list_price
```

---

## 3) Real-World Use Case

### Amazon e-commerce analytics
Business question:  
“Top 20 products by net revenue in Prime customers from Tier-1 cities during last 90 days.”

With star schema:
- Query fact_order_line
- Join dim_customer + dim_product + dim_date
- Aggregate line_amount

This is typically much faster than deeply normalized OLTP joins.

---

## 4) When to Use / When NOT to Use

### Use when
- Read-heavy analytical workloads
- BI dashboards, slicing/dicing, ad-hoc SQL
- Need understandable model for analysts and product teams
- Need conformed dimensions across multiple facts

### Avoid when
- Pure transactional OLTP system
- Heavy row-level updates with strict write latency
- Extremely sparse semi-structured raw ingestion without curated model

---

## 5) Advantages & Disadvantages

### Advantages
- Fewer joins; simpler SQL
- Better query performance for aggregates
- Friendly for BI tools and self-serve analytics
- Easy to communicate to non-DB engineers

### Disadvantages
- Data redundancy in dimensions
- ETL/ELT complexity for SCD and surrogate keys
- Requires disciplined grain definition
- Potential storage overhead

---

## 6) Common Mistakes

1. **Wrong grain** (e.g., order-level fact when product analysis needs line-level)
2. Fact table stores descriptive attributes (city/product_name) instead of keys
3. Missing surrogate keys in dimensions
4. Joining fact-to-fact directly (causes explosion)
5. Over-snowflaking dimensions and losing star simplicity

---

## 7) Performance Considerations

- Partition large facts by date (or event_date)
- Cluster/sort by high-cardinality join keys where engine supports it
- Keep dimensions narrow for hot columns used in filters
- Use integer surrogate keys for joins
- Build summary tables/materialized views for repeated KPI queries
- Watch for skewed keys (e.g., huge “unknown” bucket)

---

## 8) 🔥 Interview Questions

### Conceptual
1. Why is star schema usually faster for analytics than 3NF?
2. Why are dimensions denormalized in star schema?
3. What is a conformed dimension?

### Scenario-based
1. You modeled fact_orders at order header grain, but product-level conversion analysis is now required. What changes?
2. Revenue dashboard is slow despite star schema. What 5 things do you check first?

### Product-based (Amazon/Uber/Netflix)
1. Design a star schema for Uber rides and explain grain.
2. Design watch-time analytics star for Netflix with device and title dimensions.
3. Explain how Prime membership history impacts Amazon customer dimension design.

### Follow-ups
- How do you handle late-arriving dimensions?
- When would you introduce aggregate fact tables?
- How do you avoid double counting in multi-join scenarios?
