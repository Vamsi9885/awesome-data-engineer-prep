# 🧪 CASE STUDY - Ride Sharing (Uber-style)

## Scenario
You support city operations analytics for ride-sharing platform.

## Sample Data
| ride_id | driver_id | rider_id | city | ride_start           | fare | status    |
|--------:|----------:|---------:|------|----------------------|-----:|-----------|
| 1       | 11        | 901      | BLR  | 2024-02-01 09:00:00  | 220  | completed |
| 2       | 11        | 902      | BLR  | 2024-02-01 09:40:00  | 150  | completed |
| 3       | 11        | 903      | BLR  | 2024-02-01 11:30:00  | 300  | completed |
| 4       | 12        | 904      | BLR  | 2024-02-01 10:00:00  | 100  | cancelled |
| 5       | 12        | 905      | BLR  | 2024-02-01 10:45:00  | 180  | completed |
| 6       | 13        | 906      | MUM  | 2024-02-01 09:20:00  | 260  | completed |

## Tasks (7)
1. Completed rides by city/day  
2. Driver earnings leaderboard  
3. Cancellation rate by city  
4. Top N drivers per city  
5. Sessionization by driver activity gap  
6. Rolling 3-ride average fare per driver  
7. Detect gaps and islands in driver active days

## Solutions
```sql
-- 1
SELECT city, DATE(ride_start) d, COUNT(*) completed_rides
FROM rides
WHERE status='completed'
GROUP BY city, DATE(ride_start);
```

```sql
-- 2
SELECT driver_id, SUM(fare) earnings
FROM rides
WHERE status='completed'
GROUP BY driver_id
ORDER BY earnings DESC;
```

```sql
-- 3
SELECT city,
  100.0*SUM(CASE WHEN status='cancelled' THEN 1 ELSE 0 END)/COUNT(*) cancel_rate
FROM rides
GROUP BY city;
```

```sql
-- 4 Top 2 drivers per city
SELECT city, driver_id, earnings
FROM (
  SELECT city, driver_id, SUM(fare) earnings,
         ROW_NUMBER() OVER (PARTITION BY city ORDER BY SUM(fare) DESC) rn
  FROM rides
  WHERE status='completed'
  GROUP BY city, driver_id
) t
WHERE rn<=2;
```

```sql
-- 5 Sessionization (30 mins)
WITH x AS (
  SELECT *,
         LAG(ride_start) OVER (PARTITION BY driver_id ORDER BY ride_start) prev_t
  FROM rides
),
y AS (
  SELECT *,
         CASE WHEN prev_t IS NULL OR ride_start-prev_t>INTERVAL '30 minute' THEN 1 ELSE 0 END new_s
  FROM x
)
SELECT *, SUM(new_s) OVER (PARTITION BY driver_id ORDER BY ride_start) session_id
FROM y;
```

```sql
-- 6 rolling 3-ride avg
SELECT driver_id, ride_id, fare,
       AVG(fare) OVER (PARTITION BY driver_id ORDER BY ride_start ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) avg_3
FROM rides;
```

```sql
-- 7 gaps and islands skeleton (active-day streaks)
-- derive day sequence and group by date - row_number offset pattern
```

## Variations / Edge Cases
- Surge multipliers.
- Cross-city driver shifts.
- Fraudulent repeated cancellations.

## Performance Considerations
- Index `(city, status, ride_start, driver_id)`.
- Partition by ride date.
- Aggregate in hourly/day marts for ops dashboards.

## 🔥 Interview Questions
**Basic:** cancellation rate query.  
**Advanced:** sessionization and streak logic.  
**Product scenario:** supply-demand mismatch diagnosis.  
**Follow-up:** real-time vs batch metrics consistency.

## Common Mistakes
- Mixing cancelled fares in earnings.
- No deterministic ordering in windows.
- Missing city partition in rank use-cases.
