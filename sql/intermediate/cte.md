# 🟡 CTE (WITH Clause) - Netflix Watch Analytics

## 1. Problem Statement
Find top users by watch time in the last 30 days, excluding test accounts, using readable layered SQL.

## 2. Sample Data
| user_id | watch_date  | minutes_watched | account_type |
|--------:|-------------|----------------:|--------------|
| 1       | 2024-02-01  | 60              | paid         |
| 2       | 2024-02-01  | 20              | paid         |
| 1       | 2024-02-02  | 45              | paid         |
| 3       | 2024-02-02  | 100             | test         |
| 2       | 2024-02-03  | 80              | paid         |
| 4       | 2024-02-03  | 30              | paid         |
| 1       | 2024-02-04  | 120             | paid         |

## 3. SQL Query
```sql
WITH filtered AS (
  SELECT user_id, minutes_watched
  FROM watch_history
  WHERE watch_date >= CURRENT_DATE - INTERVAL '30 day'
    AND account_type <> 'test'
),
agg AS (
  SELECT user_id, SUM(minutes_watched) AS total_minutes
  FROM filtered
  GROUP BY user_id
)
SELECT user_id, total_minutes
FROM agg
ORDER BY total_minutes DESC
LIMIT 3;
```

## 4. Explanation
CTEs split complex logic into understandable blocks: filter -> aggregate -> rank output.

## 5. Variations / Edge Cases
- Recursive CTE for hierarchies.
- Replace repeated subqueries with one CTE.
- Edge: engine may inline CTE (optimizer dependent).

## 6. Performance Considerations
- Index on `(watch_date, account_type, user_id)`.
- Avoid unnecessary CTE layers.
- For repeated access patterns, use materialized intermediate tables.

## 7. 🔥 Interview Questions
**Basic:** What is CTE?  
**Advanced:** CTE vs subquery tradeoffs in optimization.  
**Product Scenario:** multi-step retention metric with reusable filtered datasets.  
**Follow-up:** when CTE hurts performance, recursive depth controls.

## Common Mistakes
- Treating all CTEs as materialized by default.
- Creating deep CTE chains with unused columns.
- Missing filters in earliest possible CTE.
