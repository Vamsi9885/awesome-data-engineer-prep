# 🔄 Slowly Changing Dimensions (SCD)

## 1) Concept Explanation

Dimensions (customer, driver, title metadata) change over time.  
SCD strategies define **how to preserve or overwrite history**.

Interview framing:
- Business asks both “latest view” and “as-of-time” view
- Type choice is product requirement, not only engineering preference
- Most enterprise analytics use **Type 2** for historical correctness

---

## 2) Text-Based Diagrams

### 2.1 Type 1 (overwrite)

```text
Before
customer_id | city
------------|------
123         | Bangalore

After change
customer_id | city
------------|------
123         | Delhi   (Bangalore lost)
```

### 2.2 Type 2 (new row per change)

```text
customer_key | customer_id | city       | effective_date | end_date    | is_current
-------------|-------------|------------|----------------|-------------|-----------
1001         | 123         | Bangalore  | 2023-01-01     | 2024-03-14  | false
1088         | 123         | Delhi      | 2024-03-15     | 9999-12-31  | true
```

### 2.3 Point-in-time join

```text
fact_orders.order_date BETWEEN dim_customer.effective_date AND dim_customer.end_date
```

---

## 3) Real-World Use Case

### Amazon customer analytics
Requirement:
- “What was Prime revenue from Bangalore customers in 2023?”

If customer moved city in 2024, Type 1 breaks this analysis.  
Type 2 preserves historical context needed for reliable KPI reporting.

### Uber driver compliance
Driver’s city/vehicle category changes; compliance and earnings audits require historical state.

### Netflix profile segmentation
Content preference bucket changes over time; growth teams need past-state cohorts.

---

## 4) SCD Types (0, 1, 2, 3, 4, 6)

## Type 0 (Retain Original)
- Never changes after initial load
- Use: immutable attributes (signup_channel initial source)
- Risk: stale for truly changing attributes

## Type 1 (Overwrite)
- Update existing row; no history
- Use: typo fixes, non-analytic corrections
- Not for historical trend analytics

## Type 2 (Add New Row) ✅ Most important
- New surrogate-key row for each significant change
- Columns: effective_date, end_date, is_current, version
- Best for point-in-time reporting and compliance

## Type 3 (Previous Value Column)
- Keep current + previous (limited history)
- Use for “before/after” small-window comparisons

## Type 4 (History Table)
- Current table + separate history table
- Useful when current lookups are hot and history is rarely queried

## Type 6 (Hybrid 1+2+3)
- Combines full history + current overwrite + previous value
- Powerful but more complex ETL and semantics

---

## 5) SCD Type 2 Implementation in SQL (Warehouse)

```sql
-- Example: dim_customer(customer_key, customer_id, city, tier, effective_date, end_date, is_current, attr_hash)

-- 1) Stage incoming records with hash
WITH staged AS (
  SELECT
      s.customer_id,
      s.city,
      s.tier,
      MD5(CONCAT(COALESCE(s.city,''), '|', COALESCE(s.tier,''))) AS new_hash
  FROM stg_customer s
),
current_dim AS (
  SELECT *
  FROM dim_customer
  WHERE is_current = TRUE
),
changed AS (
  SELECT s.*
  FROM staged s
  JOIN current_dim d
    ON s.customer_id = d.customer_id
  WHERE s.new_hash <> d.attr_hash
),
new_customers AS (
  SELECT s.*
  FROM staged s
  LEFT JOIN current_dim d
    ON s.customer_id = d.customer_id
  WHERE d.customer_id IS NULL
)

-- 2) Expire changed current rows
UPDATE dim_customer d
SET end_date = CURRENT_DATE - INTERVAL '1 day',
    is_current = FALSE
WHERE d.is_current = TRUE
  AND EXISTS (
    SELECT 1
    FROM changed c
    WHERE c.customer_id = d.customer_id
  );

-- 3) Insert new rows for changed + new customers
INSERT INTO dim_customer
(customer_key, customer_id, city, tier, effective_date, end_date, is_current, attr_hash)
SELECT
  NEXTVAL('customer_key_seq'),
  x.customer_id,
  x.city,
  x.tier,
  CURRENT_DATE,
  DATE '9999-12-31',
  TRUE,
  x.new_hash
FROM (
  SELECT * FROM changed
  UNION ALL
  SELECT * FROM new_customers
) x;
```

---

## 6) SCD Type 2 Implementation in Spark (Hash + insert/expire)

```python
from pyspark.sql import functions as F

# Current active dimension rows
dim_current = (
    spark.table("dim_customer")
    .filter(F.col("is_current") == True)
    .select("customer_key", "customer_id", "city", "tier", "effective_date", "end_date", "is_current", "attr_hash")
)

# Incoming updates
stg = spark.table("stg_customer").select("customer_id", "city", "tier")

# Hash comparison
stg_h = stg.withColumn(
    "new_hash",
    F.sha2(F.concat_ws("|", F.coalesce("city", F.lit("")), F.coalesce("tier", F.lit(""))), 256)
)

joined = stg_h.alias("s").join(dim_current.alias("d"), on="customer_id", how="left")

changed = joined.filter((F.col("d.customer_id").isNotNull()) & (F.col("s.new_hash") != F.col("d.attr_hash")))
new_recs = joined.filter(F.col("d.customer_id").isNull())

# Expire old records for changed customers
expired_updates = (
    changed.select("d.*")
    .withColumn("end_date", F.date_sub(F.current_date(), 1))
    .withColumn("is_current", F.lit(False))
)

# New active rows (for changed + new customers)
new_active_from_changed = changed.select(
    F.col("s.customer_id").alias("customer_id"),
    F.col("s.city").alias("city"),
    F.col("s.tier").alias("tier"),
    F.current_date().alias("effective_date"),
    F.lit("9999-12-31").cast("date").alias("end_date"),
    F.lit(True).alias("is_current"),
    F.col("s.new_hash").alias("attr_hash")
)

new_active_from_new = new_recs.select(
    F.col("s.customer_id").alias("customer_id"),
    F.col("s.city").alias("city"),
    F.col("s.tier").alias("tier"),
    F.current_date().alias("effective_date"),
    F.lit("9999-12-31").cast("date").alias("end_date"),
    F.lit(True).alias("is_current"),
    F.col("s.new_hash").alias("attr_hash")
)

# Keep untouched current rows
untouched = dim_current.join(
    changed.select(F.col("s.customer_id").alias("cid")).distinct(),
    dim_current.customer_id == F.col("cid"),
    "left_anti"
)

final_dim = (
    untouched
    .unionByName(expired_updates.select(untouched.columns))
    .unionByName(new_active_from_changed.select(untouched.columns))
    .unionByName(new_active_from_new.select(untouched.columns))
)

# Write strategy: MERGE preferred in Delta/Iceberg/Hudi for atomicity
final_dim.write.mode("overwrite").saveAsTable("dim_customer_next")
```

---

## 7) When to Use / When NOT to Use

### Use Type 2 when
- Historical reporting matters
- Regulatory/compliance traceability needed
- Product asks “as of date” metrics

### Avoid Type 2 when
- Attribute changes are non-business-critical
- Storage/complexity constraints dominate
- Only current snapshot is required

---

## 8) Advantages & Disadvantages

### Advantages
- Historical correctness
- Enables point-in-time analysis
- Supports auditability

### Disadvantages
- More storage
- More complex ETL and joins
- Harder late-arriving data handling

---

## 9) Common Mistakes

1. Missing effective_date/end_date/is_current columns
2. Using natural key in fact instead of surrogate dimension key
3. Not hashing tracked attributes for change detection
4. Over-tracking every attribute change
5. Incorrect PIT join condition causing duplicate facts
6. Late-arriving updates rewriting history incorrectly

---

## 10) Performance Considerations

- Partition/cluster by is_current, effective_date, business key where useful
- Keep current subset in fast-access view/table
- Use MERGE in ACID table formats (Delta/Iceberg/Hudi)
- Avoid full-table rewrites; process incrementally
- Maintain compact surrogate keys for fact joins
- Index/sort on business key + date range for PIT joins

---

## 11) 🔥 Interview Questions

### Conceptual
1. Type 1 vs Type 2: how to choose?
2. Why does Type 2 need surrogate keys?
3. What is point-in-time correctness?

### Scenario-based
1. Customer city changed twice in one day. How do you model effective windows?
2. Late-arriving update says city changed last month. How do you repair dimension history?
3. Your Type 2 dimension doubled unexpectedly. What checks do you run?

### Product-based
1. Amazon: design customer SCD2 for Prime/tier/city changes.
2. Uber: driver profile changes with compliance audit requirements.
3. Netflix: user subscription plan transitions and cohort backtesting.

### Follow-ups
- How do you prevent overlapping date ranges per business key?
- How would you implement SCD2 in Spark streaming + batch reconciliation?
- When does Type 4 beat Type 2?

---

## 12) Quick Type Selection Matrix

```text
Need full history?           -> Type 2
Need only current correction?-> Type 1
Need current + previous only?-> Type 3
Need split current/history?  -> Type 4
Need hybrid flexibility?     -> Type 6
Immutable attribute?         -> Type 0
