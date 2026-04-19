# 🟡 RANKING BASICS - Amazon Category Leaderboard

## 1. Problem Statement
Return top 2 products by revenue in each category for merchandising dashboards.

## 2. Sample Data
| category | product_id | revenue |
|----------|-----------:|--------:|
| Mobile   | 11         | 50000   |
| Mobile   | 12         | 65000   |
| Mobile   | 13         | 65000   |
| Laptop   | 21         | 80000   |
| Laptop   | 22         | 70000   |
| Laptop   | 23         | 60000   |
| Audio    | 31         | 15000   |
| Audio    | 32         | 18000   |

## 3. SQL Query
```sql
WITH ranked AS (
  SELECT
      category,
      product_id,
      revenue,
      ROW_NUMBER() OVER (PARTITION BY category ORDER BY revenue DESC, product_id) AS rn,
      RANK()       OVER (PARTITION BY category ORDER BY revenue DESC) AS rnk,
      DENSE_RANK() OVER (PARTITION BY category ORDER BY revenue DESC) AS drnk
  FROM product_revenue
)
SELECT category, product_id, revenue, rn, rnk, drnk
FROM ranked
WHERE rn <= 2;
```

## 4. Explanation
- `PARTITION BY category` resets ranking per category.
- `ROW_NUMBER` gives unique sequence; `RANK` leaves gaps on ties; `DENSE_RANK` no gaps.
- `rn <= 2` returns top-N per group deterministically.

## 5. Variations / Edge Cases
- Top N per group using `RANK <= N` to keep ties.
- Latest record per user: rank by timestamp desc and keep `rn=1`.
- Tie-breakers should be explicit (`ORDER BY revenue DESC, product_id`).

## 6. Performance Considerations
- Indexing: `(category, revenue DESC)`.
- Reduce input rows with date filter before window.
- Window sort cost can be high; consider pre-aggregated marts.

## 7. 🔥 Interview Questions
**Basic:** Difference between ROW_NUMBER, RANK, DENSE_RANK.  
**Advanced:** Top N per group with and without ties.  
**Product Scenario:** top drivers per city, top products per category, latest app event per user.  
**Follow-up:** deterministic ordering, skew handling, memory pressure during sorts.

## Common Mistakes
- Missing partition causes global ranking.
- Unstable tie handling due to missing secondary ORDER BY.
- Filtering before window when logic needs full group context.
