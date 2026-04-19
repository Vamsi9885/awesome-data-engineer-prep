# 🧠 RUNNING TOTALS & ROLLING AVERAGES

## 1. Problem Statement
Compute cumulative daily revenue and 3-day rolling average for finance dashboard.

## 2. Sample Data
| order_date  | daily_revenue |
|-------------|--------------:|
| 2024-02-01  | 1000          |
| 2024-02-02  | 1200          |
| 2024-02-03  | 900           |
| 2024-02-04  | 1500          |
| 2024-02-05  | 800           |
| 2024-02-06  | 1600          |

## 3. SQL Query
```sql
SELECT
    order_date,
    daily_revenue,
    SUM(daily_revenue) OVER (
      ORDER BY order_date
      ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_total,
    AVG(daily_revenue) OVER (
      ORDER BY order_date
      ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS rolling_avg_3d
FROM daily_sales
ORDER BY order_date;
```

## 4. Explanation
Frame clauses define aggregation window:
- Running total: from first row to current.
- Rolling average: last 3 rows including current.

## 5. Variations / Edge Cases
- Partition by store/city for per-group cumulative totals.
- Sparse dates: fill date spine before rolling windows.
- Use RANGE frames cautiously with duplicates.

## 6. Performance Considerations
- Index/order on `order_date`.
- Pre-aggregate to daily grain before windows.
- Large windows can be expensive; consider summary tables.

## 7. 🔥 Interview Questions
**Basic:** running total query syntax.  
**Advanced:** ROWS vs RANGE frame differences.  
**Product scenario:** daily GMV trend + anomaly detection with rolling baseline.  
**Follow-up:** missing dates, timezone cutoffs, incremental refresh.

## Common Mistakes
- Omitting ORDER BY in window.
- Wrong frame leading to incorrect totals.
- Applying rolling logic on raw transactional table directly.
