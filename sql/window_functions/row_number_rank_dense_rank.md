# 🧠 ROW_NUMBER, RANK, DENSE_RANK - High-Frequency Interview Patterns

## 1. Problem Statement
Cover top interview asks: **Second Highest Salary (with window)**, **Top N per group**, **Latest record per user**, **Deduplication**.

## 2. Sample Data
| emp_id | emp_name | salary |
|------:|----------|-------:|
| 1     | A        | 120000 |
| 2     | B        | 90000  |
| 3     | C        | 120000 |
| 4     | D        | 80000  |
| 5     | E        | 70000  |

| user_id | event_time           | event_type | event_id |
|--------:|----------------------|------------|---------:|
| 10      | 2024-02-01 10:00:00  | login      | 1        |
| 10      | 2024-02-01 10:00:00  | login      | 2        |
| 10      | 2024-02-02 09:00:00  | view       | 3        |
| 11      | 2024-02-01 12:00:00  | login      | 4        |
| 11      | 2024-02-03 12:00:00  | purchase   | 5        |
| 12      | 2024-02-02 08:00:00  | login      | 6        |

## 3. SQL Query

### A) Second Highest Salary (with window)
```sql
SELECT salary AS second_highest_salary
FROM (
  SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) AS dr
  FROM employees
) t
WHERE dr = 2;
```

### B) Top N per group (Top 2 users by total spend in each city)
```sql
WITH user_spend AS (
  SELECT city, user_id, SUM(amount) AS total_spend
  FROM orders
  GROUP BY city, user_id
),
ranked AS (
  SELECT *,
         ROW_NUMBER() OVER (PARTITION BY city ORDER BY total_spend DESC, user_id) AS rn
  FROM user_spend
)
SELECT * FROM ranked WHERE rn <= 2;
```

### C) Latest record per user
```sql
SELECT user_id, event_time, event_type
FROM (
  SELECT *,
         ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY event_time DESC, event_id DESC) AS rn
  FROM user_events
) t
WHERE rn = 1;
```

### D) Dedup using ROW_NUMBER
```sql
SELECT user_id, event_time, event_type, event_id
FROM (
  SELECT *,
         ROW_NUMBER() OVER (
           PARTITION BY user_id, event_time, event_type
           ORDER BY event_id
         ) AS rn
  FROM user_events
) d
WHERE rn = 1;
```

## 4. Explanation
Window functions retain row-level detail while adding ranking metadata by partition and order.

## 5. Variations / Edge Cases
- `RANK` includes ties with gaps.
- `DENSE_RANK` includes ties without gaps.
- Deterministic tie-breakers required for stable output.

## 6. Performance Considerations
- Index partition/order keys (e.g., `(user_id, event_time DESC)`).
- Reduce data early with date predicates.
- Large partitions can spill memory during sorts.

## 7. 🔥 Interview Questions
**Basic:** ROW_NUMBER vs RANK vs DENSE_RANK?  
**Advanced:** dedup strategy with deterministic ordering.  
**Product scenario:** latest customer state, top sellers per category.  
**Follow-up:** tie handling, skewed partitions, incremental computation.

## Common Mistakes
- Missing PARTITION BY -> global ranking bug.
- No tie-breaker in ORDER BY.
- Using subqueries where windows are clearer/faster.
