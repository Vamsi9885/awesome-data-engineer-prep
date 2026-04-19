# 💾 Storage Formats Comparison

## 1. Concept Explanation

**Production Reality:**
```
CSV: Human readable → Never use in prod
JSON: Flexible → Schema chaos
Parquet: Columnar → 10x faster analytics
Avro: Schema evolution → Streaming king
ORC: Hive optimized → Similar to Parquet
```

**Key Metrics:**
- Compression ratio
- Query speed  
- Schema enforcement
- Ecosystem support

## 2. Real-World Example - Netflix Viewing Data

```
Netflix Daily Pipeline (1TB/day):
❌ CSV: 1TB → $50/day S3
✅ Parquet Snappy: 120GB → $6/day S3
✅ + Partitioning: 20x query speedup
```

## 3. Code Examples

### PySpark Write Comparison
```python
# Same dataset, different formats
df.write.mode("overwrite") \
  .partitionBy("date") \
  .parquet("s3://netflix/viewing/parquet/")  # 95% compression
  
df.write.mode("overwrite") \
  .json("s3://netflix/viewing/json/")        # 60% compression

# Read performance
spark.read.parquet("...").count()   # 2s
spark.read.json("...").count()      # 45s
```

### AWS Athena Cost Comparison
```sql
-- Same query, different formats
SELECT * FROM parquet_table WHERE date = '2024-01-01';
-- Scanned: 50MB, Cost: $0.001

SELECT * FROM json_table WHERE date = '2024-01-01';  
-- Scanned: 2GB, Cost: $0.04
```

## 4. Real-Time Production Scenario

**Swiggy Order Processing (10M orders/day):**

```
Kafka → Spark Streaming → Delta Lake
1. Avro (schema registry) from Kafka
2. Parquet (Z-order clustered) to S3  
3. Delta Lake (ACID + time travel)
4. Athena queries for analytics

Result: 99.9% uptime, $0.02/query
```

## 5. Common Mistakes

| Format | Mistake | Cost |
|--------|---------|------|
| CSV | Nested data | Pipeline failures |
| JSON | No schema | Data quality issues |
| Parquet | No partitioning | Billion-row scans |
| Avro | No registry | Schema drift |

## 6. Performance Tips

```
🏆 Production Tier List:

S-Tier: Parquet + Snappy + Partitioning + Z-order
A-Tier: Delta Lake / Iceberg (ACID tables)
B-Tier: ORC (Hive ecosystems)
C-Tier: Avro (streaming only)
F-Tier: CSV/JSON (prototyping only)
```

**Compression Benchmarks (1GB dataset):**
```
Parquet Snappy: 120MB (12x)
Parquet GZIP: 80MB (12.5x) 
ORC ZLIB: 90MB (11x)
JSON: 400MB (2.5x)
CSV: 980MB (1x)
```

## 7. 🔥 Interview Questions

### Amazon L5
**Q1: Why Parquet over JSON for 1TB analytics dataset?**
```
A: Columnar storage → 10x scan reduction
   Predicate pushdown → Filter before read
   Nested support → No flattening needed
   Compression → 10x storage savings
```

**Q2 Follow-up: Partitioning strategy for order data?**
```
A: date (daily), region (100), category (50)
MAX 10K partitions/table
```

### Uber L4
**Q3: Design storage for 10M rides/day real-time analytics**
```
A: 
1. Kafka Avro → Bronze (raw)
2. Parquet Delta → Silver (cleaned) 
3. Iceberg → Gold (aggregated)
Partition: date, city
```

**Q4: CSV pipeline failing randomly. Fix?**
```
A: Schema-on-read → NULL explosions
   Solution: Parquet + schema enforcement
```

### Flipkart Scenario-Based
**Q5: S3 costs doubled after migrating to JSON. Why?**
```
A: No columnar compression
   Full table scans on filters
   Fix: Parquet + partitioning = 80% savings
```

**Q6: Schema changed mid-day. How to handle?**
```
A: Avro + Schema Registry
   Backward/forward compatible changes
   No reprocessing needed
```

---

**💰 Pro Tip:** Storage format choice = 70% of pipeline cost. Always benchmark!
