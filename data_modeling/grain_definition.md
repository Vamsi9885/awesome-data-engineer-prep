# 🎯 Grain Definition

## 1) Concept Explanation

**Grain** is the exact meaning of one row in a fact table.  
If grain is ambiguous, every metric can become wrong.

Interview framing:
- Grain is the first design decision for any fact
- Every measure and dimension relationship must be valid at that grain
- Bad grain causes double counting, missing detail, and broken business trust

---

## 2) Text-Based Diagrams

### 2.1 Two possible grains for sales

```text
Option A: fact_order (grain = 1 row per order)
-----------------------------------------------
order_id
customer_key
date_key
order_total

Option B: fact_order_line (grain = 1 row per order line item)
--------------------------------------------------------------
order_line_id
order_id
customer_key
product_key
date_key
quantity
line_amount
```

If you need “top products”, Option B is required.

### 2.2 Grain statement template

```text
This fact table stores one row per <event> per <level> per <time scope>.
```

Example:
“One row per completed Uber trip per rider-driver pair at trip completion timestamp.”

---

## 3) Real-World Use Case

### Amazon orders
PM asks:
- AOV by order (order grain)
- product attach rate (line grain)
- shipment SLA (shipment grain)

Single fact grain may not satisfy all; design multiple facts where needed.

### Netflix
One row per view event vs one row per user-day watch summary leads to very different analysis capabilities.

---

## 4) When to Use / When NOT to Use

### Use detailed (low-level) grain when
- Need flexible downstream slicing
- Unknown future analytics questions likely
- High-fidelity product analysis required

### Use higher (aggregated) grain when
- Performance/cost constraints are strict
- Questions are fixed and stable
- Data volume of raw events is too large for direct BI use

### Avoid
- Mixing multiple grains in one fact table
- Creating summary-only fact without base granular source

---

## 5) Advantages & Disadvantages

## Fine grain
### Advantages
- Maximum analytical flexibility
- Correct dimensional filtering
- Better root-cause analysis

### Disadvantages
- Higher storage and compute cost
- More ETL complexity

## Coarse grain
### Advantages
- Faster simple dashboards
- Smaller data footprint

### Disadvantages
- Limited drill-down
- Potential inability to answer new questions

---

## 6) Common Mistakes

1. Grain not documented explicitly
2. Combining measures from different grains in one row
3. Joining dimensions not valid for that grain
4. Using DISTINCT as a “fix” for duplicate metrics
5. Loading periodic snapshots into transaction grain fact (or vice versa) without separation

---

## 7) Performance Considerations

- Keep base granular fact partitioned by date
- Build aggregate tables for heavy recurring queries
- Define semantic layer metrics tied to specific grain
- Enforce grain checks in data tests (row uniqueness constraints)
- Avoid accidental fan-out joins by key auditing

---

## 8) 🔥 Interview Questions

### Conceptual
1. What is grain in a fact table?
2. Why should grain be defined before dimensions/measures?
3. Can one business process have multiple fact tables with different grains?

### Scenario-based
1. Sales dashboard shows inflated revenue after joining product dim. How do you debug grain mismatch?
2. You modeled one row per order but need item-level return analysis. Redesign?
3. For Uber, choose grain for surge pricing analysis and justify.

### Product-based
1. Define grain for Amazon sales, returns, and shipment facts.
2. Define grain for Uber trips with cancellations and partial refunds.
3. Define grain for Netflix watch analytics (event-level vs user-day summary).

### Follow-ups
- How do you test grain correctness in pipelines?
- Transaction fact vs periodic snapshot fact vs accumulating snapshot fact?
- When do you keep both fine and aggregate grains?
