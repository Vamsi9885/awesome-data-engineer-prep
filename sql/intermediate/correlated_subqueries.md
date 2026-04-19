# 🟡 CORRELATED SUBQUERIES - Uber Driver Benchmarking

## 1. Problem Statement
Find rides where fare is above that driver’s own average fare (personal performance outliers).

## 2. Sample Data
| ride_id | driver_id | ride_date   | fare_amount | city   |
|--------:|----------:|-------------|------------:|--------|
| 1       | 301       | 2024-02-01  | 120         | BLR    |
| 2       | 301       | 2024-02-02  | 180         | BLR    |
| 3       | 301       | 2024-02-03  | 90          | BLR    |
| 4       | 302       | 2024-02-01  | 200         | BLR    |
| 5       | 302       | 2024-02-02  | 240         | BLR    |
| 6       | 302       | 2024-02-03  | 100         | BLR    |

## 3. SQL Query
```sql
SELECT r1.ride_id, r1.driver_id, r1.fare_amount
FROM rides r1
WHERE r1.fare_amount >
(
    SELECT AVG(r2.fare_amount)
    FROM rides r2
    WHERE r2.driver_id = r1.driver_id
);
```

## 4. Explanation
Inner query is evaluated per outer row based on matching `driver_id`; compares each ride to driver’s baseline.

## 5. Variations / Edge Cases
- Replace with window function for better scale:
```sql
SELECT *
FROM (
  SELECT ride_id, driver_id, fare_amount,
         AVG(fare_amount) OVER (PARTITION BY driver_id) AS driver_avg
  FROM rides
) t
WHERE fare_amount > driver_avg;
```
- Edge: drivers with one ride (no outlier context).

## 6. Performance Considerations
- Correlated subqueries can be expensive on big tables.
- Prefer window rewrite when possible.
- Index `rides(driver_id, fare_amount)`.

## 7. 🔥 Interview Questions
**Basic:** What is correlated subquery?  
**Advanced:** Why is it slower sometimes than joins/windows?  
**Product Scenario:** detect anomalous high fares by driver/city/day.  
**Follow-up:** convert to CTE/window, handle skewed drivers.

## Common Mistakes
- Missing correlation condition -> full-table average bug.
- Ignoring partition dimensions like city/date.
- No index on correlated key.
