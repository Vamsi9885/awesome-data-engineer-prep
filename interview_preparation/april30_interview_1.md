# 🚀 Data Engineering Interview Prep — Real Questions, Clean Answers

> Questions sourced from actual interviews. Each answer includes concept explanation + working example.

---

## 📚 Table of Contents

1. [Python Fundamentals](#python-fundamentals)
2. [Problem Solving](#problem-solving)
3. [SQL](#sql)
4. [PySpark / Big Data](#pyspark--big-data)
5. [Scenario-Based: Employee + Salary](#scenario-based-employee--salary)

---

## 🐍 Python Fundamentals

### 1. What is an Algorithm?

An **algorithm** is a finite, ordered set of well-defined instructions to solve a problem or accomplish a task.

Key properties:
- **Input** — takes zero or more inputs
- **Output** — produces at least one output
- **Definiteness** — each step is unambiguous
- **Finiteness** — terminates after a finite number of steps
- **Effectiveness** — each step is feasible

```python
# Example: Algorithm to find the maximum value in a list
def find_max(numbers):
    if not numbers:
        return None
    max_val = numbers[0]
    for num in numbers[1:]:
        if num > max_val:
            max_val = num
    return max_val

print(find_max([3, 1, 9, 5, 7]))  # Output: 9
```

---

### 2. What are the Types of Linked Lists?

| Type | Description |
|------|-------------|
| Singly Linked | Each node points to next only |
| Doubly Linked | Each node points to next AND previous |
| Circular Singly | Last node's next points to head |
| Circular Doubly | Both directions + last node connects back to head |

```python
# Singly Linked List implementation
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class SinglyLinkedList:
    def __init__(self):
        self.head = None

    def append(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            return
        current = self.head
        while current.next:
            current = current.next
        current.next = new_node

    def display(self):
        elements = []
        current = self.head
        while current:
            elements.append(current.data)
            current = current.next
        return " -> ".join(map(str, elements))

ll = SinglyLinkedList()
ll.append(1)
ll.append(2)
ll.append(3)
print(ll.display())  # Output: 1 -> 2 -> 3
```

---

### 3. How is Memory Managed in Python?

Python uses **automatic memory management** via:

1. **Reference Counting** — every object tracks how many references point to it. When count hits 0, memory is freed immediately.
2. **Garbage Collector (gc module)** — handles **cyclic references** that reference counting alone cannot break.
3. **Memory Pools (PyMalloc)** — Python maintains pools for small objects (< 512 bytes) to reduce OS allocation overhead.

```python
import sys
import gc

# Reference counting example
x = [1, 2, 3]
print(sys.getrefcount(x))  # At least 2 (x + argument to getrefcount)

y = x  # ref count increases
print(sys.getrefcount(x))  # 3

del y  # ref count decreases
print(sys.getrefcount(x))  # Back to 2

# Forcing garbage collection for cyclic refs
gc.collect()

# Check memory size of an object
print(sys.getsizeof([1, 2, 3]))  # e.g., 88 bytes
```

---

### 4. What is Slicing?

**Slicing** extracts a sub-sequence from sequences (lists, strings, tuples) using `[start:stop:step]` notation.

- `start` — inclusive index (default: 0)
- `stop` — exclusive index (default: end)
- `step` — increment (default: 1)

```python
data = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

print(data[2:6])      # [2, 3, 4, 5]       — elements index 2 to 5
print(data[:4])       # [0, 1, 2, 3]        — first 4 elements
print(data[7:])       # [7, 8, 9]           — from index 7 to end
print(data[::2])      # [0, 2, 4, 6, 8]     — every 2nd element
print(data[::-1])     # [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]  — reversed

# String slicing
s = "DataEngineering"
print(s[0:4])         # "Data"
print(s[-11:])        # "Engineering"

# Slicing creates a NEW object (shallow copy)
original = [1, 2, 3]
copy = original[:]
copy.append(99)
print(original)  # [1, 2, 3] — unaffected
```

---

### 5. What are the Types of Scopes in Python? (LEGB Rule)

Python resolves variable names using the **LEGB** rule in order:

| Scope | Description |
|-------|-------------|
| **L**ocal | Inside the current function |
| **E**nclosing | In the enclosing function (closures) |
| **G**lobal | At the module/script level |
| **B**uilt-in | Python's built-in names (len, print, etc.) |

```python
x = "global"  # Global scope

def outer():
    x = "enclosing"  # Enclosing scope

    def inner():
        x = "local"  # Local scope
        print(x)     # Local is found first

    inner()          # Output: local
    print(x)         # Output: enclosing

outer()
print(x)             # Output: global

# Modifying outer scope with 'global' and 'nonlocal'
counter = 0

def increment():
    global counter
    counter += 1

increment()
print(counter)  # 1

def outer_fn():
    val = 10
    def inner_fn():
        nonlocal val
        val += 5
    inner_fn()
    print(val)  # 15

outer_fn()
```

---

### 6. What are Shallow Copy and Deep Copy? When to Use Each?

| | Shallow Copy | Deep Copy |
|--|-------------|-----------|
| **What** | New container, same object references | Fully independent copy of everything |
| **Nested objects** | Shared (changes affect both) | Independent (no sharing) |
| **Performance** | Faster | Slower (recursive) |
| **Use when** | Immutable inner objects, performance-critical | Mutable nested structures |

```python
import copy

original = [[1, 2, 3], [4, 5, 6]]

# Shallow copy
shallow = copy.copy(original)
shallow[0].append(99)
print(original)  # [[1, 2, 3, 99], [4, 5, 6]] — inner list affected!

# Deep copy
original2 = [[1, 2, 3], [4, 5, 6]]
deep = copy.deepcopy(original2)
deep[0].append(99)
print(original2)  # [[1, 2, 3], [4, 5, 6]] — original untouched

# Real-world data engineering use case:
# Shallow: copying a config dict with immutable values
# Deep: cloning a nested schema/pipeline config before mutation
```

---

### 7. What are Generators and Why are They Useful?

A **generator** is a function that uses `yield` to return values one at a time, producing items **lazily** (on demand). Unlike lists, they don't hold all values in memory at once.

**Why useful in Data Engineering:**
- Processing large files / streams without loading everything into RAM
- Building data pipelines with `yield`-based composition
- Memory-efficient iteration over billions of records

```python
# Regular function — loads all into memory
def get_squares_list(n):
    return [x**2 for x in range(n)]  # Full list in RAM

# Generator — lazy evaluation
def get_squares_gen(n):
    for x in range(n):
        yield x**2  # One value at a time

import sys

list_ver = get_squares_list(1_000_000)
gen_ver = get_squares_gen(1_000_000)

print(sys.getsizeof(list_ver))  # ~8MB+
print(sys.getsizeof(gen_ver))   # ~200 bytes

# Real DE pattern: reading a large CSV line by line
def read_large_file(filepath):
    with open(filepath, "r") as f:
        for line in f:
            yield line.strip()

# Generator pipeline
def parse(records):
    for r in records:
        yield r.split(",")

def filter_active(records):
    for r in records:
        if r[-1] == "active":
            yield r

# records = read_large_file("data.csv")
# active_records = filter_active(parse(records))
```

---

### 8. What is Pickling and Unpickling?

**Pickling** is the process of serializing a Python object into a byte stream. **Unpickling** is deserializing it back into a Python object.

Used for: saving model state, caching objects, inter-process communication.

```python
import pickle

# Any Python object
data = {
    "pipeline": "etl_v2",
    "config": {"batch_size": 1000, "retries": 3},
    "schema": ["id", "name", "amount", "ts"]
}

# Pickle (serialize) to file
with open("pipeline_config.pkl", "wb") as f:
    pickle.dump(data, f)

# Unpickle (deserialize)
with open("pipeline_config.pkl", "rb") as f:
    loaded = pickle.load(f)

print(loaded["pipeline"])  # etl_v2
print(loaded["config"])    # {'batch_size': 1000, 'retries': 3}

# In-memory pickle (bytes)
serialized = pickle.dumps(data)
restored = pickle.loads(serialized)

# ⚠️ Warning: Never unpickle data from untrusted sources — security risk
```

---

## 🧠 Problem Solving

### 9. Print All Prime Numbers till N — Time Complexity & Optimization

#### Naive Approach — O(n√n)

```python
def primes_naive(n):
    def is_prime(num):
        if num < 2:
            return False
        for i in range(2, int(num**0.5) + 1):
            if num % i == 0:
                return False
        return True

    return [x for x in range(2, n+1) if is_prime(x)]

print(primes_naive(50))
# [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
```

**Time complexity:** O(n√n) — for each of n numbers, we check up to √n divisors.

#### Optimized — Sieve of Eratosthenes — O(n log log n)

```python
def sieve_of_eratosthenes(n):
    if n < 2:
        return []

    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False

    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            # Mark all multiples of i as not prime
            for j in range(i*i, n+1, i):
                is_prime[j] = False

    return [i for i, prime in enumerate(is_prime) if prime]

print(sieve_of_eratosthenes(50))
# [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
```

**Time complexity:** O(n log log n) — much faster for large n.  
**Space complexity:** O(n) — stores boolean array of size n.

| Approach | Time | Notes |
|----------|------|-------|
| Trial division (naive) | O(n√n) | Simple, slow for large n |
| Sieve of Eratosthenes | O(n log log n) | Best general-purpose |
| Segmented Sieve | O(n log log n), O(√n) space | For memory-constrained environments |

---

## 🗄️ SQL

### 10. How do you Find the Employee with the Highest Salary?

```sql
-- Basic approach
SELECT employee_id, name, salary
FROM employees
ORDER BY salary DESC
LIMIT 1;
```

#### Why do we need a JOIN in this scenario?

If employee info and salary are in separate tables:

```sql
-- employees table: employee_id, name, dept_id
-- salaries table: employee_id, salary, effective_date

SELECT e.employee_id, e.name, s.salary
FROM employees e
JOIN salaries s ON e.employee_id = s.employee_id
ORDER BY s.salary DESC
LIMIT 1;
```

**JOIN is needed** because the data is normalized — keeping employee metadata and salary in separate tables avoids redundancy and anomalies.

---

### 11. What if Multiple Employees Have the Same Highest Salary?

`LIMIT 1` would arbitrarily return just one. Use a subquery or `DENSE_RANK()`:

```sql
-- Using subquery (returns ALL employees with max salary)
SELECT e.employee_id, e.name, s.salary
FROM employees e
JOIN salaries s ON e.employee_id = s.employee_id
WHERE s.salary = (
    SELECT MAX(salary) FROM salaries
);

-- Using window function (more flexible)
WITH ranked AS (
    SELECT
        e.employee_id,
        e.name,
        s.salary,
        DENSE_RANK() OVER (ORDER BY s.salary DESC) AS rnk
    FROM employees e
    JOIN salaries s ON e.employee_id = s.employee_id
)
SELECT employee_id, name, salary
FROM ranked
WHERE rnk = 1;
```

`DENSE_RANK()` vs `RANK()`: DENSE_RANK has no gaps (1,1,2), RANK has gaps (1,1,3).

---

### 12. What is the Difference Between Highest Salary and Latest Salary?

```sql
-- Highest salary: the MAX amount ever earned
SELECT employee_id, MAX(salary) AS highest_salary
FROM salaries
GROUP BY employee_id;

-- Latest salary: current/most recent salary (by date)
SELECT DISTINCT ON (employee_id)
    employee_id,
    salary AS latest_salary,
    effective_date
FROM salaries
ORDER BY employee_id, effective_date DESC;

-- Or using ROW_NUMBER (works across all SQL dialects)
WITH latest AS (
    SELECT
        employee_id,
        salary,
        effective_date,
        ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY effective_date DESC) AS rn
    FROM salaries
)
SELECT employee_id, salary AS latest_salary, effective_date
FROM latest
WHERE rn = 1;
```

**Key insight:** An employee's latest salary ≠ highest salary. Someone could have taken a pay cut, or salaries could have been corrected.

---

## ⚡ PySpark / Big Data

### 13. Explain Spark Architecture

Spark follows a **Master-Worker (Driver-Executor)** architecture:

```
┌─────────────────────────────────────────────┐
│              DRIVER PROGRAM                 │
│  SparkContext → DAG Scheduler → Task Scheduler
└──────────────────┬──────────────────────────┘
                   │ (via Cluster Manager)
       ┌───────────┴───────────┐
       ▼                       ▼
┌─────────────┐         ┌─────────────┐
│  EXECUTOR 1 │         │  EXECUTOR 2 │
│  Task | Task│         │  Task | Task│
│  Cache/Block│         │  Cache/Block│
└─────────────┘         └─────────────┘
```

**Components:**
- **Driver** — runs the `main()` function, creates SparkContext, builds the DAG, schedules tasks
- **Cluster Manager** — allocates resources (YARN, Kubernetes, Mesos, or Spark Standalone)
- **Executor** — JVM process on worker nodes that runs tasks and caches data
- **Task** — smallest unit of work, runs on a single partition

**Execution flow:**
1. Driver creates RDD/DataFrame transformations (lazy — builds DAG)
2. An **Action** (`.count()`, `.collect()`, `.write()`) triggers execution
3. DAG Scheduler splits the DAG into **stages** at shuffle boundaries
4. Task Scheduler assigns **tasks** to executors
5. Executors execute tasks and return results or write output

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("ArchDemo") \
    .getOrCreate()

# Transformation (lazy — just builds plan)
df = spark.read.csv("sales.csv", header=True, inferSchema=True)
filtered = df.filter(df["amount"] > 1000)
grouped = filtered.groupBy("region").sum("amount")

# Action (triggers actual execution)
grouped.show()
```

---

### 14. Key Spark Configurations and Their Purpose

```python
spark = SparkSession.builder \
    .appName("MyPipeline") \
    .config("spark.executor.memory", "4g") \
    .config("spark.executor.cores", "4") \
    .config("spark.executor.instances", "10") \
    .config("spark.driver.memory", "2g") \
    .config("spark.sql.shuffle.partitions", "200") \
    .config("spark.default.parallelism", "200") \
    .config("spark.memory.fraction", "0.8") \
    .config("spark.memory.storageFraction", "0.3") \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.adaptive.skewJoin.enabled", "true") \
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
    .getOrCreate()
```

| Config | Purpose |
|--------|---------|
| `executor.memory` | Heap memory per executor |
| `executor.cores` | Parallel tasks per executor |
| `sql.shuffle.partitions` | Partitions after a shuffle (default 200) — tune for data size |
| `default.parallelism` | Default partition count for RDD operations |
| `memory.fraction` | Fraction of heap for execution + storage |
| `adaptive.enabled` | AQE — dynamically optimizes query plan at runtime |
| `serializer=KryoSerializer` | Faster, smaller serialization than Java default |

---

### 15. What is Data Skew and How Do You Handle It?

**Data skew** occurs when data is unevenly distributed across partitions — one or few tasks process most of the data while others finish quickly, creating a bottleneck.

**How to detect:**
```python
# Check partition sizes
df.rdd.mapPartitionsWithIndex(
    lambda i, it: [(i, sum(1 for _ in it))]
).toDF(["partition", "count"]).show()

# Spark UI: look for straggler tasks in Stage view
```

**Solutions:**

```python
from pyspark.sql import functions as F

# 1. Salting — add random prefix to skewed key before join
salt_factor = 10

df_skewed = df_skewed.withColumn(
    "salted_key",
    F.concat(df_skewed["join_key"], F.lit("_"), (F.rand() * salt_factor).cast("int"))
)

df_large = df_large.withColumn("salt", F.explode(F.array([F.lit(i) for i in range(salt_factor)])))
df_large = df_large.withColumn(
    "salted_key",
    F.concat(df_large["join_key"], F.lit("_"), df_large["salt"].cast("string"))
)

result = df_skewed.join(df_large, "salted_key")

# 2. Broadcast join (when one side is small < 10MB)
from pyspark.sql.functions import broadcast

result = large_df.join(broadcast(small_df), "key")

# 3. AQE Skew Join (Spark 3.x — automatic)
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")

# 4. Repartition on a more granular key
df.repartition(200, "region", "date")

# 5. Custom partitioner — repartition skewed key
df.repartitionByRange(200, "salary")
```

---

## 🏢 Scenario-Based: Employee + Salary Tables

### Schema

```sql
-- employees table
CREATE TABLE employees (
    employee_id   INT PRIMARY KEY,
    name          VARCHAR(100),
    department    VARCHAR(50),
    joining_date  DATE
);

-- salaries table
CREATE TABLE salaries (
    salary_id     INT PRIMARY KEY,
    employee_id   INT,
    salary        DECIMAL(10, 2),
    effective_date DATE,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);
```

### Part 1: Find Employee with Highest Salary

```sql
-- SQL: handles ties
WITH max_salary AS (
    SELECT MAX(salary) AS top_salary FROM salaries
),
top_employees AS (
    SELECT s.employee_id, e.name, s.salary
    FROM salaries s
    JOIN employees e ON s.employee_id = e.employee_id
    JOIN max_salary m ON s.salary = m.top_salary
)
SELECT * FROM top_employees;
```

### Part 2: Fetch Full Salary History from Joining Date

```sql
-- Get all salary records for the highest-paid employee
-- from their joining date onwards
WITH max_emp AS (
    SELECT e.employee_id, e.name, e.joining_date
    FROM employees e
    JOIN salaries s ON e.employee_id = s.employee_id
    WHERE s.salary = (SELECT MAX(salary) FROM salaries)
    LIMIT 1  -- if multiple, pick one; remove LIMIT for all
)
SELECT
    me.employee_id,
    me.name,
    s.salary,
    s.effective_date
FROM salaries s
JOIN max_emp me ON s.employee_id = me.employee_id
WHERE s.effective_date >= me.joining_date
ORDER BY s.effective_date;
```

---

### Part 3: Solve in PySpark

```python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window

spark = SparkSession.builder.appName("EmpSalaryAnalysis").getOrCreate()

# Load data
employees = spark.read.parquet("employees.parquet")
salaries = spark.read.parquet("salaries.parquet")

# Step 1: Find highest salary
max_salary = salaries.agg(F.max("salary").alias("max_salary")).collect()[0]["max_salary"]

# Step 2: Get employee(s) with that salary
top_emp = salaries.filter(F.col("salary") == max_salary) \
    .join(employees, "employee_id") \
    .select("employee_id", "name", "joining_date") \
    .distinct()

# Step 3: Fetch salary history from joining date
result = salaries.join(top_emp, "employee_id") \
    .filter(F.col("effective_date") >= F.col("joining_date")) \
    .select("employee_id", "name", "salary", "effective_date") \
    .orderBy("employee_id", "effective_date")

result.show()
```

---

### Part 4: Optimize for Large-Scale Data

```python
from pyspark.sql import functions as F
from pyspark.sql.window import Window

# 1. Use broadcast join if employees table is small
from pyspark.sql.functions import broadcast

# 2. Avoid collect() for max — use join instead
max_salary_df = salaries.agg(F.max("salary").alias("max_salary"))

top_emp = salaries.join(max_salary_df, salaries["salary"] == max_salary_df["max_salary"]) \
    .join(broadcast(employees), "employee_id") \
    .select("employee_id", "name", "joining_date") \
    .distinct()

# 3. Partition salaries by employee_id for efficient filtering
salaries_partitioned = salaries.repartition(200, "employee_id")

# 4. Persist top_emp if reused
top_emp.cache()

# 5. Fetch salary history
result = salaries_partitioned.join(top_emp, "employee_id") \
    .filter(F.col("effective_date") >= F.col("joining_date")) \
    .select("employee_id", "name", "salary", "effective_date") \
    .orderBy("employee_id", "effective_date")

# 6. Write as partitioned parquet for downstream consumption
result.write \
    .mode("overwrite") \
    .partitionBy("employee_id") \
    .parquet("output/salary_history/")

# 7. Enable AQE
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
```

**Optimization checklist for large-scale:**
- ✅ Broadcast small tables
- ✅ Avoid `collect()` — keep operations distributed
- ✅ Partition data by join key
- ✅ Enable AQE (Adaptive Query Execution)
- ✅ Use Parquet (columnar + predicate pushdown)
- ✅ Cache reused DataFrames
- ✅ Tune `spark.sql.shuffle.partitions` based on data volume

---

## 💡 Quick Reference Summary

| Topic | Key Takeaway |
|-------|-------------|
| Algorithm | Finite steps: input → process → output |
| Linked Lists | Singly, Doubly, Circular variants |
| Memory (Python) | Ref counting + GC for cycles + PyMalloc pools |
| Slicing | `[start:stop:step]` — creates new object |
| LEGB | Local → Enclosing → Global → Built-in |
| Shallow vs Deep Copy | Shallow shares inner refs; Deep is fully independent |
| Generators | Lazy, memory-efficient iteration with `yield` |
| Pickling | Serialize Python objects to byte streams |
| Sieve of Eratosthenes | O(n log log n) prime generation |
| SQL Highest Salary | Use `DENSE_RANK()` or subquery for ties |
| Spark Architecture | Driver + Cluster Manager + Executors |
| Data Skew | Salting, Broadcast join, AQE, Repartition |

---

*📌 Star this repo if it helped. PRs welcome for corrections or additions.*
