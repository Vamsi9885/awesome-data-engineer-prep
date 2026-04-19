# ⚡ SQL Performance Optimization

## 1. Concept Explanation

**90% of DE interviews = "Make this query 10x faster"**

```
Bad Query: 10min execution
Good Query: 30s execution
Great Query: 3s execution + scales to 1TB
```

**Optimization Layers:**
1. **Query rewrite** (80% gains)
2. **Indexes** (10x gains)  
3. **Partitioning** (100x gains)
4. **Materialized views** (1000x gains)

## 2. Real-World Example - Uber Dashboard

```
Before: 15min query → Dashboard timeout
After: 12s query → Real-time dashboard
```

## 3. Code Examples

### Query Rewrite Patterns
```sql
-- ❌ SLOW (Correlated subquery)
SELECT o.order_id
FROM orders o
WHERE o.amount > (
    SELECT AVG(amount) 
    FROM orders o2 
    WHERE o2.customer_id = o.customer_id
);

-- ✅ FAST (Window function)
SELECT order_id
FROM (
    SELECT *,
           AVG(amount) OVER (PARTITION BY customer_id) as avg_amount
    FROM orders
) t
WHERE amount > avg_amount;
```

### Index Strategy (Production)
```sql
-- Composite index (most important!)
CREATE INDEX idx_orders_customer_date_status 
ON orders (customer_id, order_date, status);

-- Covering index (avoid table lookup)
CREATE INDEX idx_rides_covering 
ON rides (driver_id, trip_date) INCLUDE (fare, rating);
```

### EXPLAIN Analysis
```sql
-- Run this FIRST always!
EXPLAIN (ANALYZE, BUFFERS) 
SELECT * FROM orders 
WHERE customer_id = 123 
  AND order_date >= '2024-01-01'
  AND status = 'completed';
```

## 4. Real-Time Production Scenario

**Amazon Seller Reports (1B orders):**

```
Problem: Daily report takes 2hrs
Solution:
1. Partition switch (date) → 1min
2. Composite index → 10s  
3. Materialized view → 1s

Cost: $100/day → $0.10/day
```

## 5. Common Mistakes

| Anti-Pattern | Cost | Fix |
|--------------|------|-----|
| `SELECT *` | 10x memory | Specific columns |
| `LIKE '%text'` | No index | Full-text search |
| Functions in WHERE | Index miss | Pre-compute |
| OR conditions | Index miss | UNION ALL |

## 6. Performance Checklist

```
🏆 Production Optimization Framework:

1. EXPLAIN first (Seq Scan = BAD)
2. Filter > Join > Group > Window
3. Composite indexes ((a,b,c))
4. LIMIT 1000 during dev
5. Partition large tables
6. Materialize expensive aggregations

Query Plan Red Flags:
❌ Seq Scan          <- Add index
❌ Nested Loop       <- Rewrite JOIN  
❌ HashAggregate     <- Pre-aggregate
❌ 1B rows planned   <- Partition!
```

## 7. 🔥 Interview Questions

### Amazon L5
**Q1: This query scans 1TB. Fix it.**
```sql
-- Given:
SELECT * FROM orders WHERE YEAR(order_date) = 2024;

-- Fix:
SELECT * FROM orders WHERE order_date >= '2024-01-01' 
                       AND order_date < '2025-01-01';
-- + Partition by date
```

**Q2: Index for this query?**
```sql
SELECT * FROM orders 
WHERE customer_id = 123 
  AND status = 'completed' 
  AND order_date >= '2024-01-01';
```
```
A: CREATE INDEX ON orders(customer_id, status, order_date);
```

### Uber L4
**Q3: 10M rides table, city filter slow.**
```
A: 
1. Composite: (city, trip_date)
2. Partition: trip_date  
3. Z-order: pickup_lat, pickup_lng
```

**Q4: Subquery vs CTE vs Window?**
```
A: Window > CTE > Subquery (performance)
   Window > Subquery (readability)
```

### Flipkart Production
**Q5: Dashboard timeout at 5min. Architecture fix?**
```
A: 
1. Materialized view (hourly refresh)
2. Partitioned fact table
3. Pre-aggregated metrics
4. Covering indexes
```

**Q6: EXPLAIN shows Hash Join. Problem?**
```
A: Skewed data → Broadcast small table
   Or sort-merge with good indexes
```

---

**⚡ Pro Tip:** 80% optimization = query rewrite. Indexes give 10x, partitioning 100x.
```sql
-- Bookmark this:
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) SELECT ...;
