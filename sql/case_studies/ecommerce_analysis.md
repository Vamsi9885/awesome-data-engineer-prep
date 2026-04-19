# 🧪 CASE STUDY - E-commerce Analysis (Amazon-style)

## 1. Problem Statement
You are a Data Engineer supporting Amazon’s Daily Business Review. Build production-style SQL answers for growth, retention, and conversion.

## 2. Sample Data

### orders
| order_id | customer_id | order_date  | category | amount | status    | city      |
|---------:|------------:|-------------|----------|-------:|-----------|-----------|
| 1        | 1001        | 2024-02-01  | Mobile   | 1200   | delivered | Bengaluru |
| 2        | 1002        | 2024-02-01  | Audio    | 300    | delivered | Mumbai    |
| 3        | 1001        | 2024-02-02  | Mobile   | 800    | delivered | Bengaluru |
| 4        | 1003        | 2024-02-03  | Laptop   | 1500   | cancelled | Delhi     |
| 5        | 1004        | 2024-02-03  | Laptop   | 2000   | delivered | Mumbai    |
| 6        | 1002        | 2024-02-04  | Audio    | 450    | delivered | Mumbai    |
| 7        | 1005        | 2024-02-04  | Mobile   | 950    | delivered | Bengaluru |
| 8        | 1006        | 2024-02-05  | Home     | 600    | delivered | Pune      |

### events (for funnel)
| user_id | event_time           | event_name   |
|--------:|----------------------|--------------|
| 1001    | 2024-02-01 09:00:00  | product_view |
| 1001    | 2024-02-01 09:05:00  | add_to_cart  |
| 1001    | 2024-02-01 09:10:00  | purchase     |
| 1002    | 2024-02-01 10:00:00  | product_view |
| 1002    | 2024-02-01 10:03:00  | add_to_cart  |
| 1003    | 2024-02-01 10:30:00  | product_view |

## 3. SQL Queries + 4. Explanation

### Task 1: Daily GMV
```sql
SELECT order_date, SUM(amount) AS gmv
FROM orders
WHERE status = 'delivered'
GROUP BY order_date
ORDER BY order_date;
```
**Why:** Delivered-only revenue; daily aggregation supports dashboards.

### Task 2: Top N per group (Top 2 customers by city)
```sql
WITH city_spend AS (
  SELECT city, customer_id, SUM(amount) AS spend
  FROM orders
  WHERE status='delivered'
  GROUP BY city, customer_id
),
ranked AS (
  SELECT *,
         ROW_NUMBER() OVER (PARTITION BY city ORDER BY spend DESC, customer_id) rn
  FROM city_spend
)
SELECT city, customer_id, spend
FROM ranked
WHERE rn <= 2;
```
**Why:** Canonical top-N-per-group using window ranking.

### Task 3: Latest record per user
```sql
SELECT customer_id, order_id, order_date, amount
FROM (
  SELECT *,
         ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC, order_id DESC) rn
  FROM orders
) t
WHERE rn = 1;
```

### Task 4: Cohort analysis (basic)
```sql
WITH first_order AS (
  SELECT customer_id, DATE_TRUNC('month', MIN(order_date)) AS cohort_month
  FROM orders
  WHERE status='delivered'
  GROUP BY customer_id
),
activity AS (
  SELECT customer_id, DATE_TRUNC('month', order_date) AS activity_month
  FROM orders
  WHERE status='delivered'
)
SELECT f.cohort_month, a.activity_month, COUNT(DISTINCT a.customer_id) AS active_users
FROM first_order f
JOIN activity a ON f.customer_id = a.customer_id
GROUP BY f.cohort_month, a.activity_month
ORDER BY 1,2;
```

### Task 5: Funnel analysis (view -> cart -> purchase)
```sql
SELECT
  COUNT(DISTINCT CASE WHEN event_name='product_view' THEN user_id END) AS view_users,
  COUNT(DISTINCT CASE WHEN event_name='add_to_cart' THEN user_id END) AS cart_users,
  COUNT(DISTINCT CASE WHEN event_name='purchase' THEN user_id END) AS purchase_users
FROM events;
```

### Task 6: Running totals
```sql
WITH daily AS (
  SELECT order_date, SUM(amount) AS daily_gmv
  FROM orders
  WHERE status='delivered'
  GROUP BY order_date
)
SELECT
  order_date,
  daily_gmv,
  SUM(daily_gmv) OVER (
    ORDER BY order_date
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
  ) AS running_gmv
FROM daily;
```

## 5. Variations / Edge Cases
- Refund-adjusted GMV with refunds table.
- Multi-currency normalization before aggregation.
- Late-arriving orders handled via backfill window.

## 6. Performance Considerations
- Index: `(status, order_date, city, customer_id)`.
- Partition large order fact by `order_date`.
- Build daily marts for dashboards to avoid raw table scans.
- Avoid `SELECT *`; project only required columns.

## 7. 🔥 Interview Questions
### Basic
- Difference between GMV and net revenue?
- How to compute repeat customer rate?

### Advanced
- Design cohort table incrementally.
- Top N with ties: ROW_NUMBER vs RANK behavior.

### Product-based scenario
- Conversion dropped in one city: which funnel cuts would you run first?

### Follow-up
- How to validate data quality for revenue?
- Handling canceled/returned orders consistently?
- How would you optimize this on 10B rows?

## Common Mistakes
- Including cancelled orders in GMV.
- Missing partition key in top-N query.
- No tie-breaker in ORDER BY for latest row logic.
- Recomputing full history instead of incremental models.
