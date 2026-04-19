# ❄️ Snowflake Schema

## 1) Concept Explanation

Snowflake schema is a dimensional model where dimensions are **normalized into sub-dimensions**.  
Instead of one wide denormalized dimension (star), you split hierarchical attributes into separate tables.

Interview framing:
- Star = fewer joins, simpler reads
- Snowflake = less redundancy, more hierarchy governance
- Choose based on query pattern + maintainability + performance trade-off

---

## 2) Text-Based Diagrams

### 2.1 Snowflake Layout

```text
                dim_date
                   |
dim_customer --- fact_sales --- dim_product --- dim_category --- dim_department
                   |
               dim_store --- dim_region --- dim_country
```

### 2.2 Example Structure

```text
Fact: fact_sales
----------------
sales_id
date_key
customer_key
product_key
store_key
quantity
net_amount

Dimension: dim_product
----------------------
product_key
product_id
product_name
category_key

Sub-dimension: dim_category
---------------------------
category_key
category_name
department_key

Sub-dimension: dim_department
-----------------------------
department_key
department_name
```

---

## 3) Real-World Use Case

### Netflix content taxonomy analytics
If content classification is deep and changing:
- title -> sub_genre -> genre -> content_group
- region -> country -> market

Snowflake helps maintain controlled hierarchies used by multiple marts and governance pipelines.

---

## 4) When to Use / When NOT to Use

### Use when
- Strong hierarchical dimensions (geo/product/org)
- High dimension redundancy in star is costly
- Governance and canonical hierarchy management are priority
- Reusable hierarchies across multiple subject areas

### Avoid when
- BI users need very simple and fast SQL
- Query engine struggles with many joins
- Team prioritizes dashboard speed over strict normalization

---

## 5) Advantages & Disadvantages

### Advantages
- Reduced redundancy in dimensions
- Easier maintenance of hierarchical attributes
- Better consistency for shared hierarchy tables
- Smaller dimension storage footprint

### Disadvantages
- More joins, more complex SQL
- Can be slower for ad-hoc analytics
- Harder for analysts to use directly
- BI semantic layer becomes more critical

---

## 6) Common Mistakes

1. Over-snowflaking every attribute (unnecessary complexity)
2. Applying snowflake where star would be enough
3. Poor documentation of hierarchy paths
4. No conformed keys between hierarchy tables
5. Mixing transactional normalization with warehouse snowflaking

---

## 7) Performance Considerations

- Pre-join common snowflake paths into presentation views
- Cache/cluster hierarchy tables by key
- Use query acceleration/materialized views on hot reports
- Validate cardinality to avoid join blowups
- Consider hybrid approach: core snowflake + denormalized marts

---

## 8) 🔥 Interview Questions

### Conceptual
1. Star schema vs snowflake schema: when does each win?
2. Why can snowflake be slower?
3. Is snowflake always “more correct” than star?

### Scenario-based
1. Product hierarchy changes frequently and is reused by multiple facts. Which design and why?
2. Dashboard latency increased after snowflaking a model. How do you fix it without losing hierarchy governance?

### Product-based
1. Design Uber city -> region -> country hierarchy with trips fact.
2. Design Netflix title taxonomy model where genre mapping changes quarterly.
3. For Amazon catalog analytics, where would you keep brand/category/department?

### Follow-ups
- Would you expose snowflake tables directly to analysts?
- How do you test hierarchy integrity?
- How do you evolve hierarchy keys without breaking facts?
