# 📄 File Formats Deep Dive

## 1. Concept Explanation

**Row vs Columnar - The Core Battle:**
```
Row: Transactional (OLTP) - Store complete records
Column: Analytics (OLAP) - Store columns separately

Reality: Columnar = 100x analytics speedup
```

**Key Formats:**
| Format | Storage | Use Case | Compression |
|--------|---------|----------|-------------|
| Parquet | Columnar | Analytics | 75% (Snappy) |
| Avro | Row | Streaming | 50% |
| ORC | Columnar | Hive | 70% (ZLIB) |
| JSON | Row | APIs | 40% |

**Parquet Magic:**
```
Predicate Pushdown: Filter before read
Column Pruning: Read only needed columns
Dictionary Encoding: "NYC"→1, "LA"→2
```

## 2. Real-World Example - Amazon

```
Amazon Product Catalog (10B rows):
Parquet: SELECT category, AVG(price) 
→ Reads 2 columns out of 50 = 96% less I/O

JSON equivalent: Full row scan = 25x slower
```

## 3. Practical Scenario

**Flipkart Search Analytics:**
```
Raw logs → Parquet (partitioned by date)
Query: AVG(clicks) WHERE device='mobile'
→ Column pruning + predicate pushdown = 3s vs 5min
```

## 4. Common Mistakes

| Mistake | Impact | Fix |
|---------|--------|-----|
| JSON for analytics | Full scans | Parquet |
| No compression | 5x S3 cost | Snappy/GZIP |
| Row format analytics | 100x slow | Columnar |
| Nested JSON | Schema explosion | Parquet nested |

## 5. Performance Tips

```
🏆 Format Benchmarks (1TB scan):
Parquet Snappy: 2min, $0.20
ORC ZLIB: 2.5min, $0.25
Avro: 15min, $1.50
JSON: 45min, $4.50

Pro Tip: Parquet + partitioning + Z-order = 1000x speedup
```

## 6. 🔥 Interview Questions

### Amazon L5
**Q1: Why Parquet preferred in big data?**
```
A: 1. Columnar (pruning/pushdown)
   2. Nested support 3. Compression
   4. Footer metadata (schema)
```

**Q2 Follow-up: Parquet vs ORC?**
```
A: Parquet: Universal (Spark/Athena)
   ORC: Hive-optimized (Bloom filters)
```

### Uber L4
**Q3: 10TB log analytics slow. Fix?**
```
A: Convert JSON→Parquet + partition(date)
   Expected: 50x speedup, 80% cost save
```

**Q4: Schema evolution in Parquet?**
```
A: Evolve in Spark (add columns)
   Footer updates automatically
```

### Netflix Scenario
**Q5: Parquet files 1MB each. Problems?**
```
A: S3 GET costs explode (1M objects)
   Fix: Compaction to 128MB-1GB
```

**Q6: Row vs columnar for time-series?**
```
A: Columnar (most queries aggregate)
   Exception: Point lookups → Row
```

---

**⚡ Pro Tip:** Parquet is default. Don't overthink.
