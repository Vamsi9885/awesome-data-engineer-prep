# 🔴 INDEXING - Strategy for Product Analytics

## 1. Problem Statement
Design indexing strategy for orders/payments workload supporting OLTP lookups + analytics filters.

## 2. Sample Data
| order_id | customer_id | order_date  | status    | amount |
|---------:|------------:|-------------|-----------|-------:|
| 1        | 1001        | 2024-01-01  | delivered | 500    |
| 2        | 1002        | 2024-01-01  | placed    | 900    |
| 3        | 1001        | 2024-01-02  | delivered | 700    |
| 4        | 1003        | 2024-01-03  | cancelled | 300    |
| 5        | 1004        | 2024-01-04  | delivered | 1200   |

## 3. SQL Query
```sql
-- Point lookup
SELECT order_id, amount
FROM orders
WHERE order_id = 5;

-- Composite filter
SELECT order_id, customer_id, amount
FROM orders
WHERE status = 'delivered'
  AND order_date >= '2024-01-01';
```

Recommended indexes:
```sql
CREATE UNIQUE INDEX idx_orders_pk ON orders(order_id);
CREATE INDEX idx_orders_status_date ON orders(status, order_date);
CREATE INDEX idx_orders_customer_date ON orders(customer_id, order_date DESC);
```

## 4. Explanation
- Primary key index for exact lookup.
- Composite index to support common filter order.
- Separate index for customer timeline queries.

## 5. Variations / Edge Cases
- Partial index on active statuses.
- Covering indexes to avoid heap lookups.
- Too many indexes harm write throughput.

## 6. Performance Considerations
- Measure via EXPLAIN + query stats.
- Balance read speed vs insert/update overhead.
- Rebuild/analyze stats in maintenance windows.
- Use partition + local indexes for very large tables.

## 7. 🔥 Interview Questions
**Basic:** clustered vs non-clustered index?  
**Advanced:** why index not used despite existing?  
**Product scenario:** payments table hot writes, slow reads—index strategy?  
**Follow-up:** index selectivity, cardinality, index-only scan conditions.

## Common Mistakes
- Indexing low-cardinality columns alone.
- Duplicative indexes with same leading prefix.
- Ignoring write amplification and bloat.
