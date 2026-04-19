# 🗃️ SQL Fundamentals for Data Engineers

## 1. Concept Explanation

**Production SQL != LeetCode**
```
LeetCode: 1 table, contrived data
Production: 100 tables, NULLs, duplicates, bad data
```

**Core Skills:**
- JOINs (not just INNER)
- Aggregation + HAVING
- Subqueries/CTEs
- Window functions basics
- Performance awareness

## 2. Real-World Example - Uber Rides

```
Uber Analytics Query:
"Top 10 drivers by revenue last week, excluding cancellations"
-- 5 tables, real constraints, business logic
```

## 3. Code Examples

### Essential JOIN Patterns
```sql
-- Uber: Driver earnings (most asked!)
SELECT 
    d.driver_id,
    d.name,
    COUNT(r.ride_id) as total_rides,
    SUM(r.fare_amount) as total_earnings,
    AVG(r.rating) as avg_rating
FROM drivers d
LEFT JOIN rides r ON d.driver_id = r.driver_id
    AND r.status = 'completed'  -- Business filter
    AND r.trip_date >= '2024-01-01'
WHERE d.city = 'bangalore'
GROUP BY d.driver_id, d.name
HAVING COUNT(r.ride_id) >= 10  -- Quality filter
ORDER BY total_earnings DESC
LIMIT 10;
```

### Aggregation + Window (Amazon Favorite)
```sql
-- Running total earnings (daily)
SELECT 
    driver_id,
    trip_date,
    daily_earnings,
    SUM(daily_earnings) OVER (
        PARTITION BY driver_id 
        ORDER BY trip_date 
        ROWS UNBOUNDED PRECEDING
    ) as cumulative_earnings
FROM daily_earnings
ORDER BY driver_id, trip_date;
```

## 4. Real-Time Production Scenario

**Swiggy Order Analytics (Real Query):**

```
Production Query (runs every hour):
1. JOIN 7 tables (orders, users, restaurants, payments, coupons, delivery, ratings)
2. Filter: last 7 days, status=delivered, amount>0
3. Business logic: net_amount = total - discount + tax
4. Aggregation: city-level metrics
5. Window: rank restaurants by AOV

Executes in 45s on 100M rows
```

## 5. Common Mistakes

| Mistake | Symptom | Fix |
|---------|---------|-----|
| `SELECT *` | Slow queries | Explicit columns |
| `IN (subquery)` | Cartesian explosion | EXISTS / JOIN |
| No indexes | Table scans | Composite indexes |
| Functions in WHERE | No index usage | Pre-compute |

## 6. Performance Tips

```
🏆 Production SQL Rules:

1. Filter FIRST (WHERE before JOIN)
2. LIMIT early  
3. Use EXISTS over IN
4. Avoid SELECT *
5. Index: (status, date) composite

Query Cost Formula:
rows_scanned * complexity = execution_time
```

## 7. 🔥 Interview Questions

### Amazon L4 (Basics)
**Q1: Find 2nd highest fare ride per driver**
```sql
SELECT * FROM (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY driver_id 
               ORDER BY fare DESC
           ) as rn
    FROM rides
) t WHERE rn = 2;
```

**Q2: Duplicate handling?**
```
A: COUNT(*) vs COUNT(DISTINCT), 
   ROW_NUMBER() for dedup,
   GROUP BY for aggregation
```

### Uber L5 (Real Query)
**Q3: Weekly active drivers (WAU)**
```sql
SELECT 
    DATE_TRUNC('week', trip_date) as week_start,
    COUNT(DISTINCT driver_id) as wau
FROM rides 
WHERE status = 'completed'
GROUP BY 1
ORDER BY 1;
```

**Q4 Follow-up: Only drivers with >10 rides/week?**
```sql
HAVING COUNT(*) >= 10
```

### Flipkart Scenario
**Q5: Orders table has NULLs everywhere. Clean it.**
```sql
-- Multiple approaches
COALESCE(amount, 0) as safe_amount,
CASE 
    WHEN status IS NULL THEN 'unknown'
    ELSE status 
END as clean_status
```

**Q6: Self-join use case?**
```
A: Customer lifetime value
   Manager-subordinate hierarchy
   Product bundles (order-item pairs)
```

---

**⚡ Pro Tip:** Always write `EXPLAIN ANALYZE` first in production!
```sql
EXPLAIN ANALYZE SELECT ...;
-- Look for: Seq Scan (bad), Index Scan (good)
