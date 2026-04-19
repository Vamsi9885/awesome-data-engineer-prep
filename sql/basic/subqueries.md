# 🟢 SUBQUERIES - Flipkart Order Intelligence

## 1. Problem Statement
**Scenario (Flipkart Analytics):**  
Find customers whose total spending is above platform average customer spending. Also solve **Second Highest Salary** using a non-LIMIT approach (classic interview).

---

## 2. Sample Data

**orders**
| order_id | customer_id | order_date  | amount | status    |
|---------:|------------:|-------------|-------:|-----------|
| 1        | 101         | 2024-01-01  | 500    | delivered |
| 2        | 102         | 2024-01-02  | 1200   | delivered |
| 3        | 101         | 2024-01-03  | 700    | delivered |
| 4        | 103         | 2024-01-04  | 300    | cancelled |
| 5        | 104         | 2024-01-05  | 950    | delivered |
| 6        | 102         | 2024-01-06  | 400    | delivered |
| 7        | 105         | 2024-01-06  | 200    | delivered |
| 8        | 104         | 2024-01-07  | 650    | delivered |

**employees**
| emp_id | emp_name | salary |
|-------:|----------|-------:|
| 1      | A        | 120000 |
| 2      | B        | 90000  |
| 3      | C        | 120000 |
| 4      | D        | 80000  |
| 5      | E        | 70000  |

---

## 3. SQL Query

### A) Customers above average customer spend
```sql
SELECT customer_id, customer_total
FROM (
    SELECT customer_id, SUM(amount) AS customer_total
    FROM orders
    WHERE status = 'delivered'
    GROUP BY customer_id
) t
WHERE customer_total >
(
    SELECT AVG(customer_total)
    FROM (
        SELECT customer_id, SUM(amount) AS customer_total
        FROM orders
        WHERE status = 'delivered'
        GROUP BY customer_id
    ) x
);
```

### B) Second Highest Salary (without LIMIT)
```sql
SELECT MAX(salary) AS second_highest_salary
FROM employees
WHERE salary < (SELECT MAX(salary) FROM employees);
```

---

## 4. Explanation
1. Inner aggregate computes delivered spend by customer.
2. Outer query compares each customer’s spend with global average spend.
3. Second-highest logic excludes max salary first, then takes max among remaining.
4. This avoids DB-specific syntax like LIMIT/OFFSET for portability.

---

## 5. Variations / Edge Cases

### Correlated version (same result, often slower)
```sql
SELECT DISTINCT o1.customer_id
FROM orders o1
WHERE (
    SELECT SUM(o2.amount)
    FROM orders o2
    WHERE o2.customer_id = o1.customer_id
      AND o2.status = 'delivered'
) >
(
    SELECT AVG(customer_total)
    FROM (
      SELECT customer_id, SUM(amount) AS customer_total
      FROM orders
      WHERE status = 'delivered'
      GROUP BY customer_id
    ) t
);
```

**Edge cases:**
- All salaries same → second highest is NULL.
- Cancelled orders should be excluded.
- NULL amount handling via `COALESCE(amount,0)`.

---

## 6. Performance Considerations
- Index: `orders(status, customer_id, amount)`.
- Materialize customer aggregates for frequent reporting.
- Avoid repeated same subquery by CTE/temp table in heavy workloads.
- For large employee table, index on salary helps second-highest query.

---

## 7. 🔥 Interview Questions

### Basic
- What is a subquery?
- Difference between scalar subquery and table subquery?

### Advanced
- Subquery vs CTE: readability and optimizer behavior?
- When to replace subquery with window function?

### Product-based Scenario
- Flipkart asks: find merchants whose GMV is above category median last month.

### Follow-up
1. How do NULLs affect NOT IN subqueries?
2. EXISTS vs IN performance?
3. How to debug subquery returning multiple rows?
4. What if business asks top 5% customers instead of above average?

---

## Common Mistakes
| Mistake | Fix |
|---|---|
| Using `NOT IN` with NULL-producing subquery | Use `NOT EXISTS` |
| Repeating expensive subqueries | Use CTE/materialized intermediate |
| Including cancelled/refunded orders | Filter status explicitly |
| Using SELECT * in subqueries | Select only required columns |
