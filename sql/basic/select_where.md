# 🟢 SELECT + WHERE - Amazon Inventory Check

## 1. Problem Statement
**Amazon Fulfillment Center**: Find all low-stock items (quantity < 50) in 'Seattle' warehouse that are 'active' and priced > $10. Real-world inventory management query run daily.

## 2. Sample Data

**products table:**
| product_id | name              | warehouse | quantity | price | status  |
|------------|-------------------|-----------|----------|-------|---------|
| 1          | iPhone 14         | Seattle   | 45       | 999   | active  |
| 2          | MacBook Pro       | Seattle   | 120      | 1999  | active  |
| 3          | AirPods           | Seattle   | 30       | 129   | active  |
| 4          | iPad              | Mumbai    | 60       | 599   | inactive|
| 5          | Apple Watch       | Seattle   | 25       | 399   | active  |
| 6          | Laptop Stand      | Seattle   | 200      | 25    | active  |
| 7          | Mouse             | Seattle   | 80       | 29    | active  |

## 3. SQL Query
```sql
SELECT 
    product_id,
    name,
    quantity,
    price
FROM products
WHERE warehouse = 'Seattle'
  AND quantity < 50
  AND price > 10
  AND status = 'active';
```

**Result:**
| product_id | name         | quantity | price |
|------------|--------------|----------|-------|
| 1          | iPhone 14    | 45       | 999   |
| 3          | AirPods      | 30       | 129   |
| 5          | Apple Watch  | 25       | 399   |

## 4. Explanation
1. **SELECT**: Choose specific columns (avoid SELECT * for performance).
2. **FROM**: Source table.
3. **WHERE clause**: Chain conditions with AND (evaluated left-to-right).
4. Filters applied **before** any sorting/grouping.
5. String literals in single quotes.

## 5. Variations / Edge Cases
```sql
-- Multiple conditions (OR)
WHERE warehouse IN ('Seattle', 'Mumbai')

-- NULL handling
WHERE quantity IS NULL OR quantity < 0

-- Date range (common)
WHERE created_date >= '2024-01-01' 
  AND created_date < '2024-02-01'

-- Pattern matching
WHERE name LIKE 'iPhone%'  -- Starts with
```

**Edge Cases:**
- NULL quantities: Use `quantity IS NULL`.
- Case sensitivity: Use `ILIKE` (PostgreSQL) or `LOWER()`.
- Empty results: Add `ORDER BY quantity ASC` for consistency.

## 6. Performance Considerations
- **Index**: `CREATE INDEX idx_products_warehouse_status_qty ON products(warehouse, status, quantity);`
- **Filter order**: High-selectivity first (status='active' filters most).
- **Avoid functions**: `WHERE LOWER(warehouse) = 'seattle'` prevents index use.
- **EXPLAIN**: Look for "Index Scan" not "Seq Scan".

## 7. 🔥 Interview Questions

**Basic:**
Q: Write query for products > $100.
```sql
SELECT * FROM products WHERE price > 100;
```

**Advanced:**
Q: Seattle low-stock OR Mumbai high-price items?
```sql
SELECT * FROM products 
WHERE (warehouse = 'Seattle' AND quantity < 50)
   OR (warehouse = 'Mumbai' AND price > 500);
```

**Product-based (Amazon):**
Q: Find items expiring soon (expiry_date within 30 days) with low stock.
```sql
SELECT * FROM products 
WHERE expiry_date <= CURRENT_DATE + 30 
  AND quantity < 50 
  AND status = 'active';
```

**Follow-ups:**
1. How to handle timezone in dates? `AT TIME ZONE 'UTC'`
2. Pagination? `LIMIT 20 OFFSET 0`
3. What if warehouse is NULL? `COALESCE(warehouse, 'Unknown') = 'Seattle'`
4. Performance for 1B rows? Partition by warehouse.

**Common Mistakes:**
| Mistake | Fix |
|---------|-----|
| `=` vs `IN` for single value | Use `=` (faster) |
| No quotes on strings | `'Seattle'` not `Seattle` |
| SELECT * in production | List columns |
| WHERE 1=1 always | Remove |
