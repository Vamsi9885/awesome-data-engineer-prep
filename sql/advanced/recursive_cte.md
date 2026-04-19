# 🔴 RECURSIVE CTE - Org Trees and Category Hierarchies

## 1. Problem Statement
Build category breadcrumb paths and depth from parent-child hierarchy (Amazon catalog taxonomy use case).

## 2. Sample Data
| category_id | category_name | parent_category_id |
|------------:|---------------|-------------------:|
| 1           | Electronics   | NULL               |
| 2           | Mobiles       | 1                  |
| 3           | Android       | 2                  |
| 4           | iOS           | 2                  |
| 5           | Laptops       | 1                  |
| 6           | Gaming        | 5                  |

## 3. SQL Query
```sql
WITH RECURSIVE cat_tree AS (
  SELECT
      category_id,
      category_name,
      parent_category_id,
      category_name::text AS path,
      1 AS depth
  FROM categories
  WHERE parent_category_id IS NULL

  UNION ALL

  SELECT
      c.category_id,
      c.category_name,
      c.parent_category_id,
      (ct.path || ' > ' || c.category_name) AS path,
      ct.depth + 1 AS depth
  FROM categories c
  JOIN cat_tree ct
    ON c.parent_category_id = ct.category_id
)
SELECT * FROM cat_tree
ORDER BY path;
```

## 4. Explanation
Anchor query selects roots. Recursive part expands children level by level, building path and depth.

## 5. Variations / Edge Cases
- Employee-manager hierarchy.
- Detect cycles using visited-path guards.
- Limit depth for safety (`WHERE depth <= 20`).

## 6. Performance Considerations
- Index `categories(parent_category_id)`.
- Guard against cycles/infinite recursion.
- Precompute flattened hierarchy for BI workloads.

## 7. 🔥 Interview Questions
**Basic:** What are anchor and recursive members?  
**Advanced:** How to prevent cycles?  
**Product scenario:** category pathing for browse tree and search facets.  
**Follow-up:** depth limits, cost of recursive expansion, materialization strategy.

## Common Mistakes
- Missing termination condition.
- No cycle check on dirty data.
- Not indexing parent key.
