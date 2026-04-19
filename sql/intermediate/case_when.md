# 🟡 CASE WHEN - Amazon Customer Segmentation

## 1. Problem Statement
Classify customers into value tiers (High/Medium/Low) based on delivered GMV in last 90 days for campaign targeting.

## 2. Sample Data
| customer_id | order_id | order_date  | amount | status    |
|------------:|---------:|-------------|-------:|-----------|
| 201         | 5001     | 2024-01-10  | 1200   | delivered |
| 202         | 5002     | 2024-01-12  | 300    | delivered |
| 201         | 5003     | 2024-01-14  | 800    | delivered |
| 203         | 5004     | 2024-01-16  | 150    | delivered |
| 204         | 5005     | 2024-01-18  | 2000   | delivered |
| 202         | 5006     | 2024-01-18  | 400    | cancelled |
| 205         | 5007     | 2024-01-19  | 650    | delivered |

## 3. SQL Query
```sql
WITH customer_gmv AS (
    SELECT customer_id, SUM(amount) AS gmv
    FROM orders
    WHERE status = 'delivered'
      AND order_date >= CURRENT_DATE - INTERVAL '90 day'
    GROUP BY customer_id
)
SELECT
    customer_id,
    gmv,
    CASE
        WHEN gmv >= 2000 THEN 'High Value'
        WHEN gmv >= 800 THEN 'Medium Value'
        ELSE 'Low Value'
    END AS value_segment
FROM customer_gmv;
```

## 4. Explanation
Aggregate first, classify second. CASE provides deterministic business bucketing from highest threshold to lowest.

## 5. Variations / Edge Cases
- CASE in ORDER BY for custom sort.
- Nested CASE for tier + risk.
- Handle NULL GMV with `COALESCE(gmv,0)`.

## 6. Performance Considerations
- Index on `(status, order_date, customer_id)`.
- Keep CASE deterministic and simple.
- Precompute segment tables for dashboard workloads.

## 7. 🔥 Interview Questions
**Basic:** CASE vs IF?  
**Advanced:** CASE in aggregates (`SUM(CASE WHEN ... THEN 1 END)`)  
**Product Scenario:** Segment customers for Prime upsell campaign.  
**Follow-up:** overlapping thresholds, null handling, maintainability of business rules.

## Common Mistakes
- Overlapping CASE ranges.
- Missing ELSE branch.
- Using CASE before aggregation when logic depends on aggregate.
