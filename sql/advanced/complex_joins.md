# 🔴 COMPLEX JOINS - Marketplace Reconciliation

## 1. Problem Statement
Build a reconciliation output combining orders, shipments, refunds, and payments to identify net realized revenue per order.

## 2. Sample Data
| order_id | customer_id | order_amount | order_date  |
|---------:|------------:|-------------:|-------------|
| 1        | 101         | 1000         | 2024-02-01  |
| 2        | 102         | 500          | 2024-02-01  |
| 3        | 103         | 700          | 2024-02-02  |
| 4        | 101         | 400          | 2024-02-03  |
| 5        | 104         | 1200         | 2024-02-03  |

| shipment_id | order_id | shipped_date | shipment_status |
|------------:|---------:|--------------|-----------------|
| 11          | 1        | 2024-02-02   | shipped         |
| 12          | 2        | 2024-02-03   | delayed         |
| 13          | 3        | 2024-02-03   | shipped         |

| payment_id | order_id | paid_amount | payment_status |
|-----------:|---------:|------------:|----------------|
| 91         | 1        | 1000        | success        |
| 92         | 2        | 500         | success        |
| 93         | 3        | 700         | failed         |
| 94         | 5        | 1200        | success        |

| refund_id | order_id | refund_amount |
|----------:|---------:|--------------:|
| 201       | 2        | 100           |
| 202       | 5        | 200           |

## 3. SQL Query
```sql
SELECT
    o.order_id,
    o.order_amount,
    COALESCE(p.paid_amount, 0) AS paid_amount,
    COALESCE(r.refund_amount, 0) AS refund_amount,
    s.shipment_status,
    COALESCE(p.paid_amount, 0) - COALESCE(r.refund_amount, 0) AS net_realized
FROM orders o
LEFT JOIN payments p
  ON o.order_id = p.order_id
 AND p.payment_status = 'success'
LEFT JOIN refunds r
  ON o.order_id = r.order_id
LEFT JOIN shipments s
  ON o.order_id = s.order_id;
```

## 4. Explanation
Combine fact-like tables carefully with LEFT JOIN to preserve primary grain (`order_id`), then compute derived net.

## 5. Variations / Edge Cases
- Multiple refunds/payments per order: pre-aggregate child tables before joining.
- Use FULL OUTER JOIN for full reconciliation view.
- Self-join for customer repeat purchase sequence.

## 6. Performance Considerations
- Index join keys (`order_id`) across all tables.
- Aggregate large child tables first to avoid fanout.
- Use `EXPLAIN` to inspect join order and hash join memory.

## 7. 🔥 Interview Questions
**Basic:** How to avoid duplicate amplification in multi-join query?  
**Advanced:** Pre-aggregation strategy before joins.  
**Product Scenario:** finance mismatch due to one-to-many joins.  
**Follow-up:** surrogate keys, late-arriving facts, SCD interaction.

## Common Mistakes
- Joining raw one-to-many tables without aggregation.
- Wrong join type dropping unmatched orders.
- Using SELECT * creates ambiguity and I/O bloat.
