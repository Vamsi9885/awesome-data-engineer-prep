# 🟢 GROUP BY + HAVING - Uber Driver Performance

## 1. Problem Statement
**Scenario (Uber Bangalore):**  
Operations wants a weekly leaderboard of drivers with strong activity in the last 30 days. For each driver, compute total rides, total earnings, and average fare. Only include drivers who completed at least **10 rides**.

---

## 2. Sample Data

**rides table:**

| ride_id | driver_id | city      | ride_date   | fare_amount | ride_status |
|--------:|----------:|-----------|-------------|------------:|-------------|
| 101     | 9001      | Bangalore | 2024-02-01  | 320         | completed   |
| 102     | 9001      | Bangalore | 2024-02-03  | 280         | completed   |
| 103     | 9002      | Bangalore | 2024-02-02  | 150         | completed   |
| 104     | 9001      | Bangalore | 2024-02-04  | 420         | completed   |
| 105     | 9003      | Bangalore | 2024-02-02  | 210         | cancelled   |
| 106     | 9002      | Bangalore | 2024-02-05  | 190         | completed   |
| 107     | 9002      | Bangalore | 2024-02-06  | 230         | completed   |
| 108     | 9004      | Bangalore | 2024-02-04  | 500         | completed   |
| 109     | 9001      | Bangalore | 2024-02-07  | 305         | completed   |
| 110     | 9002      | Bangalore | 2024-02-08  | 170         | completed   |

> In production, this table contains millions of rows per city/day.

---

## 3. SQL Query

```sql
SELECT
    driver_id,
    COUNT(*) AS total_completed_rides,
    SUM(fare_amount) AS total_earnings,
    AVG(fare_amount) AS avg_fare
FROM rides
WHERE city = 'Bangalore'
  AND ride_status = 'completed'
  AND ride_date >= CURRENT_DATE - INTERVAL '30 day'
GROUP BY driver_id
HAVING COUNT(*) >= 10
ORDER BY total_earnings DESC;
```

---

## 4. Explanation

1. **WHERE filters first**: keep only Bangalore + completed rides + last 30 days.
2. **GROUP BY driver_id**: aggregate metrics per driver.
3. **COUNT/SUM/AVG**:
   - `COUNT(*)` → number of completed rides
   - `SUM(fare_amount)` → total earnings
   - `AVG(fare_amount)` → average earning per ride
4. **HAVING COUNT(*) >= 10**: post-aggregation filter.
5. **ORDER BY total_earnings DESC**: leaderboard sorted by earnings.

**Why this works:**  
`WHERE` narrows the dataset before grouping (faster, correct). `HAVING` applies business rule on aggregated rows.

---

## 5. Variations / Edge Cases

### A) Show only high-quality + high-earning drivers
```sql
HAVING COUNT(*) >= 10
   AND SUM(fare_amount) >= 5000
```

### B) Month bucketed performance
```sql
SELECT
    driver_id,
    DATE_TRUNC('month', ride_date) AS ride_month,
    COUNT(*) AS rides_in_month,
    SUM(fare_amount) AS earnings_in_month
FROM rides
WHERE ride_status = 'completed'
GROUP BY driver_id, DATE_TRUNC('month', ride_date);
```

### C) Include drivers with zero completed rides (LEFT JOIN with drivers table)
Use `drivers d LEFT JOIN rides r ...` and aggregate with `COALESCE`.

**Edge cases:**
- Cancelled rides should not inflate driver performance.
- NULL fares: use `SUM(COALESCE(fare_amount, 0))`.
- Timezone-sensitive date filter: normalize to UTC before date logic.

---

## 6. Performance Considerations

- **Composite index:**  
  `CREATE INDEX idx_rides_city_status_date_driver ON rides(city, ride_status, ride_date, driver_id);`
- **Partitioning:** partition rides by `ride_date` for time-window queries.
- **Avoid SELECT \*** in aggregate reports.
- **Push filters to WHERE** (city, status, date) to reduce grouped rows.
- Validate with `EXPLAIN` / `EXPLAIN ANALYZE` for index/partition pruning.

---

## 7. 🔥 Interview Questions

### Basic
**Q1. Difference between WHERE and HAVING?**  
- `WHERE`: filters rows **before** grouping  
- `HAVING`: filters grouped/aggregated results **after** grouping

**Q2. Why can’t we write `WHERE COUNT(*) >= 10`?**  
Because aggregate functions are not available in row-level filtering stage.

### Advanced
**Q3. Find drivers whose earnings are above city average earnings per driver.**
```sql
WITH driver_earnings AS (
  SELECT driver_id, SUM(fare_amount) AS total_earnings
  FROM rides
  WHERE city = 'Bangalore' AND ride_status = 'completed'
  GROUP BY driver_id
)
SELECT *
FROM driver_earnings
WHERE total_earnings > (SELECT AVG(total_earnings) FROM driver_earnings);
```

### Product-Based Scenario (Uber)
**Q4. Build a daily quality report of active drivers with cancellation rate < 5% and avg ETA < 6 mins.**  
Follow-up: which metrics should be pre-aggregated in a reporting table?

### Follow-up Questions
1. If this query is slow on 2B rows, what will you optimize first?
2. How would you handle late-arriving rides in daily aggregates?
3. Would materialized views help here?
4. How do you test correctness of aggregation logic?

---

## Common Mistakes

| Mistake | Why It’s Wrong | Correct Approach |
|---|---|---|
| Using `HAVING city = 'Bangalore'` | City filter is row-level | Put in `WHERE` |
| Counting cancelled rides | Inflates KPI | Filter `ride_status='completed'` |
| Missing date window | Full table scan risk | Add bounded date filter |
| Using `SELECT *` with GROUP BY | Invalid / noisy output | Select only grouped + aggregated columns |
