# Data Engineering Interview Questions and Answers

# 1. Difference Between ETL and ELT

## ETL
Extract → Transform → Load

- Data is transformed before loading into the warehouse.
- Used in traditional data warehouses.
- Suitable for structured and validated data.

### Use Cases
- Banking
- Compliance reporting
- Legacy enterprise systems

---

## ELT
Extract → Load → Transform

- Data is loaded first and transformed later inside the warehouse.
- Preferred in cloud-native systems.
- Suitable for big data and analytics workloads.

### Use Cases
- AI/ML pipelines
- Streaming analytics
- Data lakehouse architectures

---

# 2. Why Modern Cloud Platforms Prefer ELT

## Advantages
- Better scalability
- Faster ingestion
- Cheap cloud storage
- Keeps raw historical data
- Supports AI/ML workloads
- Uses distributed cloud compute power

### Examples
- Databricks
- Snowflake
- BigQuery

---

# 3. Why Parquet is Better than CSV

| Feature | Parquet | CSV |
|---|---|---|
| Storage | Smaller | Larger |
| Compression | High | Low |
| Performance | Faster | Slower |
| Schema Support | Yes | No |
| Read Optimization | Columnar | Row-based |

## Advantages
- Faster Spark processing
- Better compression
- Reads only required columns
- Suitable for analytics workloads

---

# 4. Scalable PySpark Pipeline Project

## Tech Stack
- Azure Data Factory
- Databricks
- PySpark
- ADLS
- Parquet/Delta

## Challenges
- Data skew
- Small files
- Memory bottlenecks
- Long-running joins

## Solutions
- Broadcast joins
- Repartitioning
- Salting technique
- File compaction
- Incremental CDC processing

## Impact
- Reduced execution time
- Improved scalability
- Better cluster utilization

---

# 5. Handling Data Skew and Memory Bottlenecks

## Data Skew Handling
- Used salting
- Repartitioned skewed keys
- Enabled AQE

## Memory Optimization
- Avoided collect()
- Optimized caching
- Tuned executor memory
- Reduced unnecessary shuffles

---

# 6. Python Scripting for Data Enrichment

## Libraries Used
- pyspark.sql.functions
- pandas
- json
- yaml
- requests

## Transformations
- Null handling
- Deduplication
- Derived columns
- CDC hash generation
- Date standardization

## Example
```python
from pyspark.sql.functions import *

df = df.withColumn(
    "full_name",
    concat(col("first_name"), lit(" "), col("last_name"))
)
```

---

# 7. Maintaining Distributed Pipelines

## Maintainability Techniques
- Modular code
- Reusable utility functions
- YAML/JSON driven configs
- Logging and exception handling
- CI/CD integration

## Efficiency Improvements
- Partition pruning
- Broadcast joins
- Incremental loads
- AQE optimization

---

# 8. Spark Optimization Project

## Optimizations Applied
- Broadcast joins
- Partition tuning
- DataFrame caching
- File compaction
- Salting for skew handling

## Impact
- Runtime reduced from 3 hours to under 1 hour
- Reduced shuffle overhead
- Improved cluster efficiency

---

# 9. Spark Resource Allocation

## Techniques
- Dynamic allocation
- Executor memory tuning
- Shuffle partition tuning
- Autoscaling clusters

## Example
```python
spark.conf.set("spark.sql.shuffle.partitions", 400)
spark.conf.set("spark.dynamicAllocation.enabled", "true")
```

---

# 10. Strategic Partitioning and Caching

## Scenario
Large transaction joins caused heavy shuffle and recomputation.

## Solution
- Repartitioned by join key
- Cached reusable DataFrames

## Impact
- Runtime reduced from 2.5 hours to 45 minutes
- Improved executor utilization

---

# 11. Broadcast Joins in Large-Scale Systems

## Why Used
To avoid expensive shuffles while joining large and small tables.

## Example
```python
from pyspark.sql.functions import broadcast

df = large_df.join(
    broadcast(small_lookup_df),
    "product_id",
    "left"
)
```

## Impact
- Faster joins
- Reduced network movement
- Lower memory usage

---

# 12. Validating Data Accuracy

## Validations Used
- Row count checks
- Null validation
- Duplicate validation
- Schema validation
- Aggregate reconciliation
- CDC/hash validation

## Tools
- PySpark
- SQL
- Audit tables
- ADF monitoring

---

# 13. Metadata-Driven Data Quality Framework

## Strategy
- Validation rules stored in YAML/JSON
- Dynamic rule execution
- Audit logging
- Failed records sent to quarantine layer

## Example
```python
duplicate_count = df.groupBy("customer_id") \
                    .count() \
                    .filter("count > 1") \
                    .count()
```

---

# 14. SQL Window Functions

## Use Cases
- Running totals
- Rankings
- Trend analysis
- Latest record identification

## Example
```sql
SELECT 
    customer_id,
    order_date,
    sales,
    SUM(sales) OVER (
        PARTITION BY customer_id
        ORDER BY order_date
    ) AS running_total
FROM sales_data;
```

## Other Functions
- ROW_NUMBER()
- LAG()
- LEAD()
- RANK()

---

# 15. Optimizing Complex SQL Queries

## Techniques
- Filter data early
- Avoid SELECT *
- Proper indexing
- Partition pruning
- Optimize join order
- Use execution plans

## Spark Optimizations
- Broadcast joins
- Reduce shuffle
- Cache reusable datasets

---

# 16. Aggregations for Large Datasets

## Common Aggregations
- SUM()
- COUNT()
- AVG()
- GROUP BY

## Example
```sql
SELECT 
    region,
    SUM(sales) AS total_sales,
    COUNT(*) AS total_orders
FROM orders
GROUP BY region;
```

## Optimization
- Filter before aggregation
- Partition-aware grouping
- Incremental aggregation

---

# 17. Linux/Unix Commands in Data Engineering

## Common Commands
- grep
- awk
- sed
- tail -f
- find
- chmod
- crontab

## Usage
- Job monitoring
- Log analysis
- File handling
- Automation scripts

## Example
```bash
grep "ERROR" oozie.log | tail -20
```

---

# 18. SQL Query - Top Selling Products

## Query
```sql
SELECT 
    p.ProductName,
    SUM(s.Quantity) AS TotalUnitsSold
FROM Products p
JOIN Sales s
    ON p.ProductID = s.ProductID
GROUP BY p.ProductName
ORDER BY TotalUnitsSold DESC;
```

---

# 19. LEFT JOIN vs INNER JOIN

## INNER JOIN
- Returns matching records only
- Faster in many cases

## LEFT JOIN
- Returns all rows from left table
- Unmatched rows contain NULLs

## Example
```sql
SELECT p.ProductName,
       COALESCE(SUM(s.Quantity),0) AS TotalUnitsSold
FROM Products p
LEFT JOIN Sales s
ON p.ProductID = s.ProductID
GROUP BY p.ProductName;
```

---

# 20. SUM() Behavior with LEFT JOIN

## Behavior
- Products without sales still appear
- SUM(quantity) becomes NULL
- COALESCE converts NULL to 0

## Result
Unsold products appear with 0 sales.

---

# 21. Longest Substring Without Repeating Characters

## Python Solution
```python
def length_of_longest_substring(s):

    char_index = {}
    left = 0
    max_length = 0

    for right in range(len(s)):

        current_char = s[right]

        if current_char in char_index and char_index[current_char] >= left:
            left = char_index[current_char] + 1

        char_index[current_char] = right

        current_length = right - left + 1

        max_length = max(max_length, current_length)

    return max_length
```

## Complexity
- Time Complexity: O(n)
- Space Complexity: O(n)

---

# 22. Why Update char_index Outside the Condition

## Reason
We always need the latest occurrence index of the character.

## Benefit
- Keeps sliding window accurate
- Prevents stale indexes
- Maintains O(n) complexity

---

# 23. Handling Repeated Characters in Sliding Window

## Logic
When a duplicate character appears:
- Move left pointer after previous occurrence
- Update latest character index
- Recalculate window size

## Example
```python
if current_char in char_index and char_index[current_char] >= left:
    left = char_index[current_char] + 1
```

## Why max_length Remains Correct
The window is adjusted before calculating the current length, ensuring only unique characters are counted.