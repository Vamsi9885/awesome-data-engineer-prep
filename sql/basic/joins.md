# 🟢 JOINS - Amazon Orders, Customers, Payments

## 1. Problem Statement
**Scenario (Amazon Marketplace):**  
You need a daily reconciliation report that combines orders with customers and payment records. Business asks for:
1) valid paid orders,  
2) orders with missing payments,  
3) orphan payment records.

You must demonstrate **INNER, LEFT, RIGHT JOIN** patterns used in interviews.

---

## 2. Sample Data

**orders**
| order_id | customer_id | order_date  | amount | order_status |
|---------:|------------:|-------------|-------:|--------------|
| 1001     | 501         | 2024-02-01  | 1200   | placed       |
| 1002     | 502         | 2024-02-01  | 350    | placed       |
| 1003     | 503         | 2024-02-02  | 800    | shipped      |
| 1004     | 504         | 2024-02-02  | 220    | cancelled    |
| 1005     | 501         | 2024-02-03  | 150    | delivered    |
| 1006     | 507         | 2024-02-03  | 560    | placed       |

**customers**
| customer_id | customer_name | city      | is_prime |
|------------:|---------------|-----------|----------|
| 501         | Asha          | Bengaluru | true     |
| 502         | Ravi          | Mumbai    | false    |
| 503         | Priya         | Delhi     | true     |
| 504         | Karan         | Pune      | false    |
| 505         | Noor          | Chennai   | true     |
| 506         | Ishan         | Hyderabad | false    |

**payments**
| payment_id | order_id | payment_status | paid_amount | paid_at      |
|-----------:|---------:|----------------|------------:|--------------|
| 90001      | 1001     | success        | 1200        | 2024-02-01   |
| 90002      | 1002     | failed         | 0           | 2024-02-01   |
| 90003      | 1003     | success        | 800         | 2024-02-02   |
| 90004      | 1005     | success        | 150         | 2024-02-03   |
| 90005      | 1010     | success        | 999         | 2024-02-03   |

---

## 3. SQL Query

### A) INNER JOIN (paid valid order report)
```sql
SELECT
    o.order_id,
    c.customer_name,
    o.amount,
    p.paid_amount,
    p.payment_status
FROM orders o
INNER JOIN customers c
    ON o.customer_id = c.customer_id
INNER JOIN payments p
    ON o.order_id = p.order_id
WHERE p.payment_status = 'success';
```

### B) LEFT JOIN (find orders missing successful payment)
```sql
SELECT
    o.order_id,
    o.customer_id,
    o.amount,
    p.payment_status
FROM orders o
LEFT JOIN payments p
    ON o.order_id = p.order_id
   AND p.payment_status = 'success'
WHERE p.order_id IS NULL;
```

### C) RIGHT JOIN (find orphan payment rows)
```sql
SELECT
    o.order_id,
    p.payment_id,
    p.paid_amount
FROM orders o
RIGHT JOIN payments p
    ON o.order_id = p.order_id
WHERE o.order_id IS NULL;
```

---

## 4. Explanation

1. **INNER JOIN** returns only matched records across all joined tables.
2. **LEFT JOIN** preserves all left table rows (`orders`) and null-fills unmatched right side.
3. **RIGHT JOIN** preserves right table rows (`payments`), useful for orphan detection.
4. Put selective filters in join predicate or WHERE carefully (changes row retention).
5. For anti-join patterns, use `LEFT JOIN ... WHERE right_key IS NULL`.

**Why this approach works:**  
Each join type answers a different business question: matched data, missing dependencies, data integrity anomalies.

---

## 5. Variations / Edge Cases

### Alternative to RIGHT JOIN (often preferred)
```sql
SELECT
    p.payment_id, p.order_id, p.paid_amount
FROM payments p
LEFT JOIN orders o
    ON p.order_id = o.order_id
WHERE o.order_id IS NULL;
```

### Self join example (manager hierarchy pattern)
```sql
SELECT e.employee_id, e.employee_name, m.employee_name AS manager_name
FROM employees e
LEFT JOIN employees m
  ON e.manager_id = m.employee_id;
```

**Edge cases:**
- Duplicate keys in dimension table can multiply rows.
- NULL join keys never match in equality join.
- Join on non-unique business keys causes accidental fanout.

---

## 6. Performance Considerations

- Index join keys:  
  - `orders(order_id, customer_id)`  
  - `customers(customer_id)`  
  - `payments(order_id, payment_status)`
- Filter early (partition/date filters for fact tables).
- Validate join cardinality before adding more tables.
- Use `EXPLAIN` to check hash join vs nested loop behavior.
- Avoid joining huge tables before pruning by date/city/status.

---

## 7. 🔥 Interview Questions

### Basic
1. Explain INNER vs LEFT vs RIGHT JOIN with one real example each.
2. How is `LEFT JOIN ... WHERE right.id IS NULL` used?

### Advanced
3. Why does moving a predicate from `ON` to `WHERE` change LEFT JOIN results?
4. How do you prevent row explosion in many-to-many joins?

### Product-based Scenario
5. Amazon finance team reports payment totals higher than order totals. How do you debug join fanout and duplicates?

### Follow-up Questions
- When would you prefer EXISTS over JOIN?
- How to reconcile late-arriving payments?
- How to detect duplicate payments per order?
- How to test join correctness in production pipelines?

---

## Common Mistakes

| Mistake | Impact | Fix |
|---|---|---|
| Joining on wrong key (`customer_name`) | Incorrect matches | Join on stable IDs |
| Applying right-table filter in WHERE after LEFT JOIN | Converts to INNER JOIN unintentionally | Keep filter in ON where needed |
| Ignoring duplicates in dim table | Inflated counts/sums | De-duplicate source or aggregate before join |
| Using SELECT * in multi-join query | High I/O + ambiguity | Project only required columns |
