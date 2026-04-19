# 🔴 QUERY OPTIMIZATION - Slow Query Tuning Playbook

## 1. Problem Statement
A dashboard query on Uber rides is timing out at peak. Optimize without changing business result.

## 2. Sample Data
| ride_id | city | ride_date   | driver_id | fare_amount | status    |
|--------:|------|-------------|----------:|------------:|-----------|
| 1       | BLR  | 2024-02-01  | 101       | 220         | completed |
| 2       | BLR  | 2024-02-01  | 102       | 150         | completed |
| 3       | BLR  | 2024-02-02  | 101       | 300         | completed |
| 4       | MUM  | 2024-02-02  | 103       | 180         | cancelled |
| 5       | BLR  | 2024-02-03  | 101       | 250         | completed |
| 6       | BLR  | 2024-02-03  | 104       | 120         | completed |

## 3. SQL Query
### Bad
```sql
SELECT *
FROM rides
WHERE DATE(ride_date) >= '2024-02-01'
  AND LOWER(city) = 'blr'
  AND status = 'completed';
```

### Better
```sql
SELECT ride_id, ride_date, driver_id, fare_amount
FROM rides
WHERE ride_date >= '2024-02-01'
  AND city = 'BLR'
  AND status = 'completed';
```

## 4. Explanation
Avoid function-wrapped indexed columns (`DATE`, `LOWER`) in predicates; project only needed columns.

## 5. Variations / Edge Cases
- Rewrite OR into UNION ALL when selective.
- Pre-aggregate large facts by day in summary table.
- Use covering indexes where practical.

## 6. Performance Considerations
- Index: `(city, status, ride_date, driver_id)`.
- Use `EXPLAIN ANALYZE` to compare scan type and rows.
- Partition on `ride_date` for pruning.
- Verify memory for hash aggregates/sorts.

## 7. 🔥 Interview Questions
**Basic:** first steps when query is slow?  
**Advanced:** interpret EXPLAIN plan (seq scan vs index scan).  
**Product scenario:** 1TB table with SLA < 2 sec—what architecture changes?  
**Follow-up:** materialized views, caching, precomputation, skew mitigation.

## Common Mistakes
- SELECT * in BI queries.
- Non-sargable predicates.
- Missing limit/sampling during debug.
