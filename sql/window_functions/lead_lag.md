# 🧠 LEAD / LAG - Time-based Behavior Analysis

## 1. Problem Statement
Compute ride-to-ride time gaps per driver and identify long idle periods.

## 2. Sample Data
| driver_id | ride_id | ride_start_time       |
|----------:|--------:|-----------------------|
| 101       | 1       | 2024-02-01 09:00:00   |
| 101       | 2       | 2024-02-01 09:45:00   |
| 101       | 3       | 2024-02-01 12:00:00   |
| 102       | 4       | 2024-02-01 10:15:00   |
| 102       | 5       | 2024-02-01 10:50:00   |
| 102       | 6       | 2024-02-01 13:20:00   |

## 3. SQL Query
```sql
SELECT
    driver_id,
    ride_id,
    ride_start_time,
    LAG(ride_start_time) OVER (
      PARTITION BY driver_id
      ORDER BY ride_start_time
    ) AS prev_ride_time,
    EXTRACT(EPOCH FROM (
      ride_start_time -
      LAG(ride_start_time) OVER (PARTITION BY driver_id ORDER BY ride_start_time)
    )) / 60 AS gap_minutes
FROM rides;
```

## 4. Explanation
`LAG` gets previous timestamp within driver partition; difference gives gap in minutes.

## 5. Variations / Edge Cases
- Use `LEAD` to get next event.
- Flag churn risk if gap > 120 mins.
- Missing timestamps: handle with filters.

## 6. Performance Considerations
- Index `(driver_id, ride_start_time)`.
- Keep partition key low skew when possible.
- Pre-filter date range before window.

## 7. 🔥 Interview Questions
**Basic:** LEAD vs LAG usage.  
**Advanced:** session boundaries from gap logic.  
**Product scenario:** detect inactivity and workforce forecasting.  
**Follow-up:** timestamp timezone normalization, null prev rows.

## Common Mistakes
- Missing partition key.
- Unordered event times.
- Not handling first-row null from LAG.
