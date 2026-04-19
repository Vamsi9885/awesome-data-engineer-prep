# 🪟 SQL Window Functions (MOST ASKED!)

## 1. Concept Explanation

**Window = "Group BY + Keep all rows"**
```
GROUP BY: 1000 customers → 1000 aggregates
Window: 1000 customers → 1000 rows + aggregates
```

**Production Use: 80% of analytics queries**

**Frame Specs:**
- `ROWS` vs `RANGE`
- `UNBOUNDED PRECEDING` to `CURRENT ROW`
- `PARTITION BY` = new GROUP BY

## 2. Real-World Example - Amazon Customer Analytics

```
Amazon Query (L5 level):
"Rank customers by spend, show running total, compare to avg"

Result: 1 query vs 5 subqueries
```

## 3. Code Examples

### Top 3 Must-Know Patterns

```sql
-- 1. RANKING (Most common interview Q)
SELECT 
    customer_id,
    order_date,
    amount,
    RANK() OVER (
        PARTITION BY customer_id 
        ORDER BY amount DESC
    ) as order_rank
FROM orders;

-- 2. RUNNING TOTALS (Revenue dashboard)
SELECT 
    customer_id,
    order_date,
    amount,
    SUM(amount) OVER (
        PARTITION BY customer_id 
        ORDER BY order_date
        ROWS UNBOUNDED PRECEDING
    ) as running_total;

-- 3. MOVING AVERAGE (Uber pricing)
SELECT 
    driver_id,
    trip_date,
    fare,
    AVG(fare) OVER (
        PARTITION BY driver_id 
        ORDER BY trip_date 
        ROWS 6 PRECEDING  -- Last 7 days
    ) as moving_avg_fare;
```

### Advanced: Multiple Windows
```sql
-- Amazon seller dashboard (production query)
SELECT 
    seller_id,
    order_date,
    orders_count,
    revenue,
    
    -- Window 1: Daily rank
    RANK() OVER (ORDER BY revenue DESC) as daily_rank,
    
    -- Window 2: Running total
    SUM(revenue) OVER (ORDER BY order_date) as cumulative_revenue,
    
    -- Window 3: Category avg
    AVG(revenue) OVER (PARTITION BY category) as category_avg
FROM daily_seller_metrics;
```

## 4. Real-Time Production Scenario

**Netflix Viewing Analytics (500M events/day):**

```
Query: "Top shows by watch time, percentile ranking, compare to user avg"

1. Window for ranking
2. Window for percentiles  
3. Window for user comparison
4. Single pass over 1TB data

Executes in 12s vs 2min with subqueries
```

## 5. Common Mistakes

| Mistake | Result | Fix |
|---------|--------|-----|
| No `ORDER BY` in window | Random results | Always specify |
| `RANK()` vs `DENSE_RANK()` | Gaps confusion | Know the difference |
| Default frame | Wrong aggregates | Explicit `ROWS` |
| Correlated subquery | N² performance | Window function |

## 6. Performance Tips

```
🏆 Window Function Optimization:

1. Filter BEFORE window (WHERE > OVER)
2. Multiple windows = single pass
3. `ROWS` faster than `RANGE` 
4. Materialize expensive windows (CTE)

EXPLAIN shows: "WindowAgg" (good)
```

## 7. 🔥 Interview Questions (90% hit rate)

### Amazon L5 (Favorite!)
**Q1: Find top 2 orders per customer**
```sql
SELECT * FROM (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY customer_id 
               ORDER BY amount DESC
           ) as rn
    FROM orders
) WHERE rn <= 2;
```

**Q2 Follow-up: Handle ties?**
```sql
-- Use RANK() instead of ROW_NUMBER()
RANK() OVER (PARTITION BY customer_id ORDER BY amount DESC)
```

### Uber L4
**Q3: Running total of fares per driver**
```sql
SUM(fare) OVER (
    PARTITION BY driver_id 
    ORDER BY trip_time
    ROWS UNBOUNDED PRECEDING
)
```

**Q4: Compare each ride fare to driver's 7-day avg**
```sql
AVG(fare) OVER (
    PARTITION BY driver_id 
    ORDER BY trip_time 
    ROWS 6 PRECEDING
)
```

### Flipkart Advanced
**Q5: Customer cohort analysis (month-over-month retention)**
```sql
SELECT 
    cohort_month,
    month_number,
    COUNT(*) as num_customers,
    FIRST_VALUE(COUNT(*)) OVER (
        PARTITION BY cohort_month
    ) as cohort_size,
    ROUND(100.0 * COUNT(*) / FIRST_VALUE(COUNT(*)) OVER (PARTITION BY cohort_month), 2) as retention
FROM cohort_table;
```

**Q6: Percentile ranking across partitions**
```sql
PERCENT_RANK() OVER (
    ORDER BY revenue DESC
) as revenue_percentile
```

---

**⚡ Pro Tip:** Window functions = 80/20 rule of SQL mastery. Master these 5: ROW_NUMBER, RANK, SUM, AVG, LAG
