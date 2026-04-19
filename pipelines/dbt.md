# 🔮 dbt (data build tool) Mastery

## 1. Concept Explanation

**dbt = SQL Analytics Engineering**

```
Raw data → dbt models → Analytics ready
TDD for data pipelines

Git + SQL + Jinja = Version controlled transformations
```

**Core Concepts:**
- **Models** = SQL transformations
- **Tests** = Data quality
- **Snapshots** = SCD Type 2
- **Sources** = Upstream dependencies

## 2. Real-World Example - Netflix Analytics

```
Netflix dbt Project:
raw_events → bronze → silver → gold → dashboards
1500+ models, CI/CD, 99.9% quality
```

## 3. Code Examples

### Complete dbt Project Structure
```
models/
├── bronze/
│   └── src_orders.sql
├── silver/
│   └── customers.sql
└── marts/
    └── customer_orders.sql
```

### Bronze Model (Raw → Clean)
```sql
-- models/bronze/src_orders.sql
{{ config(materialized='table') }}

SELECT 
    order_id,
    customer_id,
    order_date,
    amount,
    status,
    ingested_at
FROM {{ source('raw', 'orders') }}
WHERE amount > 0  -- Basic cleaning
```

### Silver Model (Business Logic)
```sql
-- models/silver/customer_orders.sql
{{ config(materialized='table', partition_by={'field': 'order_date'}) }}

SELECT 
    c.customer_id,
    c.customer_name,
    o.order_date,
    o.amount,
    CASE 
        WHEN o.amount > 1000 THEN 'whale'
        WHEN o.amount > 100 THEN 'normal'
        ELSE 'small'
    END as customer_segment
FROM {{ ref('bronze_src_orders') }} o
JOIN {{ ref('dim_customers') }} c ON o.customer_id = c.customer_id
```

### Tests (Critical!)
```yaml
-- schema.yml
models:
  - name: customer_orders
    columns:
      - name: customer_id
        tests:
          - not_null
          - unique
      - name: amount
        tests:
          - dbt_utils.expression_is_true:
              expression: "amount > 0"
```

### Snapshot (SCD Type 2)
```sql
-- models/snapshots/customer_snapshot.sql
{% snapshot customer_snapshot %}

{{ config(
    target_schema='snapshots',
    unique_key='customer_id',
    strategy='check',
    check_cols=['city', 'is_prime']
) }}

SELECT * FROM {{ source('raw', 'customers') }}

{% endsnapshot %}
```

## 4. Real-Time Production Scenario

**Flipkart dbt Analytics Pipeline:**

```
GitHub → dbt Cloud → BigQuery
1. PR → dbt test → CI pass
2. Merge → dbt run → Production models
3. dbt docs → Data catalog

Scale: 2000 models, 50TB transformed
Quality: 99.99% test pass rate
```

## 5. Common Mistakes

| Mistake | Symptom | Fix |
|---------|---------|-----|
| No tests | Silent data issues | 80% code coverage |
| SELECT * | Schema breaks | Explicit columns |
| No sources | Upstream blind | source() everywhere |
| No docs | No lineage | dbt docs generate |

## 6. Production Checklist

```
🏆 dbt Production Setup:

1. Separate prod/dev schemas
2. CI/CD (dbt Cloud/GitHub Actions)
3. Incremental models everywhere
4. Custom macros
5. Exposure tracking

Commands:
dbt test          # Quality gate
dbt run --models +customer_orders  # Targeted
dbt docs generate # Lineage
```

## 7. 🔥 Interview Questions

### Netflix L5
**Q1: dbt incremental model strategy.**
```sql
{{ config(
    materialized='incremental',
    incremental_strategy='merge'
) }}
WHERE {% if is_incremental() %}
  order_date > (SELECT MAX(order_date) FROM {{ this }})
{% endif %}
```

**Q2: Testing pyramid.**
```
Unit: dbt test (schema.yml)
Integration: Singular tests
E2E: BI dashboard validation
```

### Spotify L4
**Q3: Macro usage.**
```sql
{% macro safe_divide(numerator, denominator) %}
  CASE WHEN {{ denominator }} = 0 THEN NULL 
       ELSE {{ numerator }} / {{ denominator }} END
{% endmacro %}
```

**Q4: Sources vs refs.**
```
source(): Upstream/raw (no lineage)
ref(): dbt models (lineage tracked)
```

### Flipkart Analytics
**Q5: 1000 model monolith.**
```
A: 
1. Sub-packages (models/marts/sales/)
2. Exposure tracking
3. dbt-mesh (multiple projects)
```

**Q6: dbt + Airflow orchestration.**
```
dbt Cloud Jobs (managed)
OR BashOperator("dbt run")
```

---

**🔮 Pro Tip:** dbt docs = Your data dictionary. Share with business!
```
https://docs.company.com → Instant trust
