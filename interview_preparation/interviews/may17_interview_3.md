# 🎯 Data Engineering Interview — Questions & Answers

> Real questions from a Data Engineering interview session. Covers SQL, Spark, Python, ETL, and Data Warehousing concepts.

---

## 📌 Table of Contents

1. [What is a Star Schema?](#1-what-is-a-star-schema)
2. [What is a Factless Fact Table?](#2-what-is-a-factless-fact-table)
3. [How do you handle null values?](#3-how-do-you-handle-null-values)
4. [How do you detect outliers in data?](#4-how-do-you-detect-outliers-in-data)
5. [What is an outlier?](#5-what-is-an-outlier)
6. [Optimizing a slow data pipeline](#6-optimizing-a-slow-and-inefficient-large-volume-data-pipeline)
7. [Analyzing product review text data](#7-analyzing-product-review-text-data)
8. [What is an RDD in Apache Spark?](#8-what-is-an-rdd-resilient-distributed-dataset-in-apache-spark)
9. [Snowflake vs Traditional SQL Data Warehouse](#9-snowflake-vs-traditional-sql-data-warehouse-architecture)
10. [Debugging file-processing pipelines](#10-best-practices-for-debugging-file-processing-pipelines)
11. [Cleaning invalid email addresses](#11-cleaning-customer-data-with-invalid-email-addresses)
12. [Dictionary → Spark DataFrame + Email Regex](#12-dictionary--spark-dataframe--email-validation-with-regex)
13. [Sales aggregation using Pandas](#13-sales-aggregation-using-pandas)
14. [Sales aggregation using Spark](#14-sales-aggregation-using-apache-spark)
15. [Fixing "unsupported operand types" in Spark](#15-fixing-unsupported-operand-types-error-in-spark)
16. [Fixing error inside groupBy().agg()](#16-fixing-error-inside-groupbyagg-in-spark)
17. [Standard deviation by subject using Spark](#17-standard-deviation-scores-per-subject-using-spark)
18. [What is ETL?](#18-what-is-etl)

---

## 1. What is a Star Schema?

A **Star Schema** is a dimensional modeling technique used in data warehouses where:
- A central **Fact Table** holds measurable, quantitative data (e.g., sales amounts, order counts)
- Surrounding **Dimension Tables** hold descriptive attributes (e.g., customer, product, date)

The name comes from the star-like shape formed when the fact table connects to all dimension tables.

**Example:**
```
         DimDate
            |
DimCustomer — FactSales — DimProduct
            |
         DimStore
```

**Key Benefits:**
- Simple and intuitive structure
- Fast query performance (fewer joins)
- Easy for BI tools to understand

---

## 2. What is a Factless Fact Table?

A **Factless Fact Table** is a fact table that contains **no numeric measures** — it only stores foreign keys to dimension tables. It captures the *occurrence* of an event rather than a measurement.

**Use Cases:**
- Tracking student attendance (event happened or not)
- Recording promotional coverage (which products were on promotion on which days)
- Logging website page views without a monetary value

**Example:**
```sql
-- StudentAttendance factless fact table
StudentKey | DateKey | CourseKey | LocationKey
```

> It answers questions like: "Did this student attend class on this date?" — no numeric fact needed.

---

## 3. How do you handle null values?

**Strategy depends on context:**

| Scenario | Approach |
|----------|----------|
| Numeric columns | Fill with mean, median, or 0 |
| Categorical columns | Fill with mode or a placeholder like `"Unknown"` |
| Time-series data | Forward-fill or backward-fill |
| Business-critical columns | Drop rows or flag for manual review |
| Sparse data | Keep nulls and use null-aware aggregations |

**In PySpark:**
```python
# Drop rows with nulls
df.dropna()

# Fill nulls
df.fillna({"age": 0, "city": "Unknown"})

# Replace using when/otherwise
from pyspark.sql.functions import when, col
df.withColumn("age", when(col("age").isNull(), 0).otherwise(col("age")))
```

**In Pandas:**
```python
df.fillna(df.mean())       # numeric
df.fillna(method='ffill')  # forward fill
df.dropna(subset=['email']) # drop rows where email is null
```

---

## 4. How do you detect outliers in data?

**Common Methods:**

### 1. IQR (Interquartile Range) Method
```python
Q1 = df['value'].quantile(0.25)
Q3 = df['value'].quantile(0.75)
IQR = Q3 - Q1
outliers = df[(df['value'] < Q1 - 1.5 * IQR) | (df['value'] > Q3 + 1.5 * IQR)]
```

### 2. Z-Score Method
```python
from scipy import stats
z_scores = stats.zscore(df['value'])
outliers = df[abs(z_scores) > 3]
```

### 3. Visual Methods
- Box plots
- Scatter plots
- Histograms

### 4. In Spark
```python
from pyspark.sql.functions import col, mean, stddev

stats = df.select(mean("value").alias("mean"), stddev("value").alias("std")).collect()[0]
df_outliers = df.filter(
    (col("value") < stats["mean"] - 3 * stats["std"]) |
    (col("value") > stats["mean"] + 3 * stats["std"])
)
```

---

## 5. What is an Outlier?

An **outlier** is a data point that significantly differs from the rest of the dataset. It lies far outside the expected range of values.

**Types:**
- **Point Outlier** — A single extreme value (e.g., salary of ₹10 Cr in a dataset where average is ₹10 LPA)
- **Contextual Outlier** — Normal globally but abnormal in context (e.g., 35°C in December)
- **Collective Outlier** — A group of values that together are anomalous

**Causes:** Data entry errors, sensor malfunctions, fraud, genuine rare events.

---

## 6. Optimizing a Slow and Inefficient Large-Volume Data Pipeline

**Step-by-step approach:**

### Step 1: Profile & Identify Bottlenecks
- Use Spark UI to identify slow stages
- Check for data skew, shuffle operations, and long GC pauses

### Step 2: Optimize Data Formats
- Switch from CSV/JSON to **Parquet** or **Delta**
- Enable columnar reads and predicate pushdown

### Step 3: Reduce Shuffles
- Use `broadcast joins` for small lookup tables
- Replace `groupBy` + `sort` with window functions where possible

### Step 4: Partition Wisely
- Partition by high-cardinality columns used in filters (e.g., date, region)
- Avoid too many small files (small file problem)
- Use `repartition()` vs `coalesce()` appropriately

### Step 5: Caching
- Cache intermediate DataFrames that are reused multiple times

### Step 6: Handle Data Skew
- Salt keys for skewed joins
- Use `skewHint` or AQE (Adaptive Query Execution) in Spark 3+

### Step 7: Infrastructure Tuning
- Right-size cluster (executor memory, cores)
- Enable dynamic allocation
- Tune `spark.sql.shuffle.partitions`

---

## 7. Analyzing Product Review Text Data

**Goal:** Extract actionable insights from subjective text.

### Step 1: Data Collection & Cleaning
- Remove duplicates, nulls, HTML tags, special characters

### Step 2: Sentiment Analysis
```python
from textblob import TextBlob

df['sentiment'] = df['review'].apply(lambda x: TextBlob(x).sentiment.polarity)
# > 0: Positive, < 0: Negative, = 0: Neutral
```

### Step 3: Topic Modeling / Keyword Extraction
- Use TF-IDF or LDA to find recurring themes
- Common themes: "delivery speed", "packaging", "quality"

### Step 4: Rating Correlation
- Correlate sentiment score with star ratings to validate model

### Step 5: Aggregated Insights
```python
df.groupby('product_id')['sentiment'].mean().sort_values()
```

### Step 6: Reporting
- Visualize sentiment trends over time
- Flag products with consistently negative reviews

---

## 8. What is an RDD (Resilient Distributed Dataset) in Apache Spark?

An **RDD** is the foundational data structure in Apache Spark — an immutable, distributed collection of objects that can be processed in parallel across a cluster.

**Key Properties:**
| Property | Description |
|----------|-------------|
| **Resilient** | Fault-tolerant via lineage graph — can recompute lost partitions |
| **Distributed** | Data split across multiple nodes |
| **Dataset** | Collection of records (any type) |

**Two Types of Operations:**
- **Transformations** (lazy): `map()`, `filter()`, `flatMap()`
- **Actions** (trigger execution): `collect()`, `count()`, `saveAsTextFile()`

```python
rdd = sc.parallelize([1, 2, 3, 4, 5])
rdd_squared = rdd.map(lambda x: x ** 2)
print(rdd_squared.collect())  # [1, 4, 9, 16, 25]
```

> Modern Spark prefers DataFrames/Datasets over RDDs for better optimization via Catalyst, but RDDs are still used for unstructured data or fine-grained control.

---

## 9. Snowflake vs Traditional SQL Data Warehouse Architecture

| Feature | Snowflake | Traditional DW (Teradata/SQL Server) |
|---------|-----------|--------------------------------------|
| **Architecture** | Cloud-native, multi-cluster shared data | Monolithic, tightly coupled |
| **Storage & Compute** | Separated (scale independently) | Coupled (scale together) |
| **Scaling** | Elastic, auto-scale virtual warehouses | Manual, expensive hardware scaling |
| **Concurrency** | Multi-cluster for workload isolation | Limited concurrency, queuing |
| **Storage Format** | Columnar (micro-partitioned) | Row or columnar depending on vendor |
| **Maintenance** | Zero (fully managed) | DBA-intensive tuning needed |
| **Pricing** | Pay-per-second compute + storage | License + hardware cost |
| **Data Sharing** | Native, cross-account | Complex ETL needed |
| **Semi-structured data** | Native JSON/Avro/Parquet support | Limited or requires preprocessing |

**When to use Snowflake:** Cloud-first teams, variable workloads, rapid scaling needs.
**When to use Traditional DW:** Existing on-prem infrastructure, strict data residency requirements.

---

## 10. Best Practices for Debugging File-Processing Pipelines

1. **Validate inputs early** — Check file existence, format, size, schema before processing
2. **Log at every stage** — Ingest, transform, load with timestamps and record counts
3. **Use checksums/hashes** — Detect file corruption or partial transfers
4. **Idempotency** — Ensure re-runs don't duplicate data (use watermarking or dedup keys)
5. **Handle schema drift** — Detect and alert on unexpected column changes
6. **Dead-letter queues** — Route bad records to a separate location for review
7. **Monitor file arrival SLA** — Alert if expected files don't arrive on time
8. **Test with edge cases** — Empty files, files with only headers, malformed rows
9. **Use try/except blocks** — Gracefully handle and log exceptions per file
10. **Audit tables** — Track which files were processed, when, and their status

---

## 11. Cleaning Customer Data with Invalid Email Addresses

```python
import re
import pandas as pd

data = {
    "name": ["Alice", "Bob", "Charlie", "David"],
    "email": ["alice@example.com", "bob@invalid", "charlie@domain.co", "david@.com"]
}
df = pd.DataFrame(data)

# Regex pattern for valid emails
email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$'

df_clean = df[df['email'].str.match(email_pattern)]
print(df_clean)
```

**Output:**
```
      name              email
0    Alice  alice@example.com
2  Charlie  charlie@domain.co
```

---

## 12. Dictionary → Spark DataFrame + Email Validation with Regex

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

spark = SparkSession.builder.appName("EmailCleaning").getOrCreate()

data = [
    ("Alice", "alice@example.com"),
    ("Bob", "bob@invalid"),
    ("Charlie", "charlie@domain.co"),
    ("David", "david@.com")
]

df = spark.createDataFrame(data, ["name", "email"])

# Regex pattern
email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$'

# Filter valid emails
df_clean = df.filter(col("email").rlike(email_regex))
df_clean.show()
```

### Regex Pattern Explained: `^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$`

| Part | Meaning |
|------|---------|
| `^` | Start of string |
| `[a-zA-Z0-9_.+-]+` | One or more valid characters before `@` |
| `@` | Literal `@` symbol |
| `[a-zA-Z0-9-]+` | Domain name (letters, digits, hyphens) |
| `\.` | Literal dot |
| `[a-zA-Z]{2,}` | TLD with at least 2 letters (e.g., `.com`, `.in`) |
| `$` | End of string |

---

## 13. Sales Aggregation Using Pandas

```python
import pandas as pd

data = {
    "Product": ["A", "B", "A", "C", "B", "A"],
    "Quantity": [10, 5, 8, 3, 7, 6],
    "Price": [100, 200, 100, 150, 200, 100],
    "Date": ["2024-01-01", "2024-01-01", "2024-01-02", "2024-01-02", "2024-01-03", "2024-01-03"]
}

df = pd.DataFrame(data)
df["TotalSales"] = df["Quantity"] * df["Price"]

result = df.groupby("Product")["TotalSales"].sum().reset_index()
result.columns = ["Product", "TotalRevenue"]
print(result)
```

**Output:**
```
  Product  TotalRevenue
0       A          2400
1       B          2600
2       C           450
```

---

## 14. Sales Aggregation Using Apache Spark

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as spark_sum

spark = SparkSession.builder.appName("SalesAggregation").getOrCreate()

data = [
    ("A", 10, 100.0, "2024-01-01"),
    ("B", 5, 200.0, "2024-01-01"),
    ("A", 8, 100.0, "2024-01-02"),
    ("C", 3, 150.0, "2024-01-02"),
]

df = spark.createDataFrame(data, ["Product", "Quantity", "Price", "Date"])
df = df.withColumn("TotalSales", col("Quantity") * col("Price"))

result = df.groupBy("Product").agg(spark_sum("TotalSales").alias("TotalRevenue"))
result.show()
```

---

## 15. Fixing "Unsupported Operand Types" Error in Spark

**Error:** `TypeError: unsupported operand type(s) for *: 'int' and 'str'`

**Cause:** Column data types are incorrect (e.g., Quantity or Price is a string).

**Fix:**
```python
from pyspark.sql.functions import col
from pyspark.sql.types import IntegerType, DoubleType

df = df.withColumn("Quantity", col("Quantity").cast(IntegerType()))
df = df.withColumn("Price", col("Price").cast(DoubleType()))
df = df.withColumn("TotalSales", col("Quantity") * col("Price"))
```

**Always validate schema before calculations:**
```python
df.printSchema()
```

---

## 16. Fixing Error Inside groupBy().agg() in Spark

**Common Error:** Using Python's built-in `sum()` instead of Spark's `sum()`.

```python
# ❌ Wrong — uses Python's built-in sum
from pyspark.sql.functions import col
df.groupBy("Product").agg(sum("TotalSales"))  # NameError or wrong result

# ✅ Correct — import Spark's sum
from pyspark.sql.functions import sum as spark_sum
df.groupBy("Product").agg(spark_sum("TotalSales").alias("TotalRevenue"))
```

**Rule:** Always import Spark SQL functions explicitly and alias them to avoid conflicts with Python builtins.

---

## 17. Standard Deviation Scores Per Subject Using Spark

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import stddev, round as spark_round

spark = SparkSession.builder.appName("StdDevBySubject").getOrCreate()

data = [
    ("Alice", "Math", 85),
    ("Bob", "Math", 90),
    ("Charlie", "Math", 78),
    ("Alice", "Science", 92),
    ("Bob", "Science", 88),
    ("Charlie", "Science", 95),
]

df = spark.createDataFrame(data, ["Student", "Subject", "Score"])

result = df.groupBy("Subject").agg(
    spark_round(stddev("Score"), 2).alias("StdDev_Score")
)
result.show()
```

**Output:**
```
+-------+------------+
|Subject|StdDev_Score|
+-------+------------+
|   Math|        6.08|
|Science|        3.51|
+-------+------------+
```

---

## 18. What is ETL?

**ETL** stands for **Extract, Transform, Load** — the foundational process in data engineering for moving data from source systems to a data warehouse or data lake.

### Extract
- Pull data from sources: databases, APIs, flat files, streams
- Handle incremental vs full loads
- Tools: ADF, Airbyte, Fivetran, custom scripts

### Transform
- Clean data (remove nulls, duplicates)
- Apply business logic (calculations, aggregations)
- Normalize/denormalize, type casting, joins
- Tools: dbt, Spark, SQL

### Load
- Write processed data to target: Data Warehouse, Data Lake, Delta Lake
- Strategies: full load, incremental (append), upsert (merge/SCD)
- Tools: Snowflake, BigQuery, Delta Lake, Synapse

### Modern Variant: ELT
In cloud-native architectures, **ELT** (Extract, Load, Transform) is preferred — raw data is loaded first, then transformed in-place using SQL (e.g., dbt on BigQuery/Snowflake).

```
Source → [Extract] → Raw Layer → [Transform] → Curated Layer → BI/Analytics
```

---

## 🔗 Connect with Me

- 🍍 LinkedIn: [www.linkedin.com/in/vamsi-krishna-pineapple]
- 💻 GitHub: [https://github.com/Vamsi9885/]

> *"Every interview is a learning opportunity — win or learn, never lose."* 🚀
