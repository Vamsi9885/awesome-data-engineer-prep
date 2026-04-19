# 🌉 Bridge Tables

## 1) Concept Explanation

Bridge tables resolve **many-to-many relationships** in dimensional models.  
Without bridge tables, many-to-many joins can double count metrics.

Interview framing:
- Fact and dimensions are usually many-to-one joins
- When a relationship is many-to-many (e.g., customer↔account, title↔genre), use bridge table
- Sometimes include allocation weights to distribute measures correctly

---

## 2) Text-Based Diagrams

### 2.1 Customer to Account (many-to-many)

```text
dim_customer      bridge_customer_account       dim_account
------------      -----------------------       -----------
customer_key  <-> customer_key            <->   account_key
                account_key
                relationship_type
                effective_date
                end_date
                allocation_pct (optional)
```

### 2.2 Fact join pattern

```text
fact_transaction
----------------
transaction_id
account_key
amount
date_key

To analyze by customer:
fact_transaction -> dim_account -> bridge_customer_account -> dim_customer
```

### 2.3 Genre bridge (Netflix-like)

```text
dim_title <-- bridge_title_genre --> dim_genre
```

---

## 3) Real-World Use Case

### Banking/fintech customer-account ownership
One account can have multiple holders; one customer can have multiple accounts.  
Bridge preserves ownership relationships and enables customer-level reporting.

### Netflix title categorization
A title can belong to multiple genres/subgenres. Bridge avoids storing repeated genre arrays in fact tables.

### Uber enterprise rides
Corporate cost centers can map to multiple departments with weighted allocation.

---

## 4) When to Use / When NOT to Use

### Use when
- Genuine many-to-many relationship exists
- Need analytically correct aggregation across both sides
- Need temporal ownership history in relationships

### Avoid when
- Relationship is actually one-to-many (simpler FK works)
- Bridge is used to patch upstream data quality issues
- Team cannot maintain weighting and SCD logic correctly

---

## 5) Advantages & Disadvantages

### Advantages
- Correct modeling of many-to-many
- Prevents schema hacks and repeated denormalized arrays
- Supports weighted attribution

### Disadvantages
- More complex joins
- Risk of double counting if not weighted
- Harder for analysts without semantic layer guidance

---

## 6) Common Mistakes

1. No allocation logic for shared ownership
2. Counting fact amount fully for each bridge match (inflation)
3. Missing effective dates in bridge when relationships change
4. Using bridge without clear business definition
5. Not documenting whether bridge is exclusive/non-exclusive

---

## 7) Performance Considerations

- Keep bridge narrow and indexed on both keys
- Add effective date filters for temporal joins
- Precompute customer-attributed facts for hot dashboards
- Use allocation_pct with clear default rules
- Validate bridge cardinality drift regularly

---

## 8) 🔥 Interview Questions

### Conceptual
1. What problem does a bridge table solve?
2. Difference between bridge table and factless fact table?
3. Why can bridge tables cause double counting?

### Scenario-based
1. One account has 2 owners and $100 transaction. How do you report customer revenue?
2. Relationship changes over time. How do you model historical ownership?
3. Dashboard totals exceed source by 40% after adding bridge joins. Debug steps?

### Product-based
1. Design customer-account bridge for Amazon co-branded credit products.
2. Design Netflix title-genre bridge with evolving taxonomy.
3. Design Uber enterprise cost allocation bridge with weighted splits.

### Follow-ups
- When do you pre-aggregate instead of joining bridge at query time?
- How do you test allocation correctness?
- Could this be solved in semantic layer only?
