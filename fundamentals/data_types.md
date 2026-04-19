# 🔤 Data Types in Data Engineering

## 1. Concept Explanation

**Why data types matter in production:**
- **Storage optimization** (TB vs GB difference)
- **Query performance** (implicit casts kill performance)
- **Cost savings** (AWS S3 compression ratios)
- **Data quality** (invalid casts = pipeline failures)

```
Wrong: VARCHAR(255) for everything
Right: INT for IDs, DATE for dates, DECIMAL(10,2) for money
```

## 2. Real-World Example - Amazon Orders

```
Amazon Order Table:
❌ Wrong:
  order_id: VARCHAR(50)     <- 10GB storage
  order_date: VARCHAR(20)   <- Slow date filters
  amount: VARCHAR(15)       <- Math errors

✅ Right:
  order_id: BIGINT          <- 1GB storage
  order_date: DATE          <- Fast partitioning
  amount: DECIMAL(10,2)     <- Precise calculations
```

## 3. Code Examples

### SQL Data Type Selection
```sql
-- Ecommerce Orders Table (Production Ready)
CREATE TABLE orders (
    order_id BIGINT PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    order_date DATE NOT NULL,
    order_time TIME,
    amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Partition by date for trillion-row tables
PARTITION BY RANGE (YEAR(order_date))
```

### PySpark Schema Definition
```python
from pyspark.sql.types import *

orders_schema = StructType([
    StructField("order_id", LongType(), False),
    StructField("customer_id", LongType(), False),
    StructField("order_date", DateType(), False),
    StructField("amount", DoubleType(), False),  # Use DecimalType for money in prod
    StructField("status", StringType(), False)
])
```

## 4. Real-Time Production Scenario

**Uber Ride Pricing Pipeline:**
```
Raw Event: {"ride_id": "123", "price": "25.50", "timestamp": "2024-01-15T10:30:00Z"}
↓
Ingestion Layer: Dynamic JSON → Schema enforcement
↓
Validation: price must be DECIMAL(6,2), timestamp → TIMESTAMP
↓
Storage: Parquet with proper types → 70% compression
↓
Query Layer: Fast aggregations without casts
```

## 5. Common Mistakes

| Mistake | Impact | Fix |
|---------|--------|-----|
| `VARCHAR` for IDs | 5x storage | `BIGINT` |
| `TEXT` for JSON | Slow queries | `JSONB` (PostgreSQL) |
| `FLOAT` for money | Precision loss | `DECIMAL(10,2)` |
| `STRING` for dates | Slow filters | `DATE`/`TIMESTAMP` |

## 6. Performance Tips

```
1. Use smallest type possible:
   INT (4B) < BIGINT (8B) < STRING (variable)

2. Compression ratios:
   Parquet: INT=95%, STRING=60%
   
3. Partitioning friendly types:
   DATE > TIMESTAMP > INT (epoch)

4. Indexable types only:
   No VARCHAR(1000) indexes!
```

## 7. 🔥 Interview Questions

### Amazon L4
**Q1: Design schema for Amazon orders table (1B rows/day)**
```
A: BIGINT ids, DATE partitioning, DECIMAL money, 
   Snappy compression, Z-order clustering
```

**Q2: Why not use FLOAT for pricing?**
```
A: 0.1 + 0.2 = 0.3000000004
   DECIMAL guarantees precision
```

### Uber L5 Follow-up
**Q3: STRING vs VARCHAR vs TEXT - when to use each?**
```
STRING: In-memory processing (Spark)
VARCHAR(N): Fixed storage (MySQL/Postgres)
TEXT: Unlimited (logs, JSON)
```

**Q4: How to handle schema evolution in production?**
```
A: Add new columns (trailing), 
   Use Avro/Protobuf, 
   Schema registry (Confluent)
```

### Flipkart Scenario
**Q5: Orders table has VARCHAR order_date. Fix performance.**
```
A: 
1. ALTER → DATE type
2. Repartition by date
3. Update queries
4. 10x query speedup expected
```

---

**💡 Pro Tip:** Always profile storage costs first! One wrong type = $10K/month extra.
