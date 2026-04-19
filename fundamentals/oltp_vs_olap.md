# 🗄️ OLTP vs OLAP

## 1. Concept Explanation

**Production Reality:**
```
OLTP: 10K TPS writes (orders)
OLAP: 1TB scans (monthly reports)

Mixing = Disaster (Amazon learned this)
```

**Detailed Comparison:**
| Aspect | OLTP (MySQL/Postgres) | OLAP (Snowflake/Redshift) |
|--------|----------------------|---------------------------|
| Workload | Many small writes | Few large reads |
| Schema | Normalized (3NF) | Denormalized (star) |
| Indexing | Many indexes | Few/minimal |
| Concurrency | ACID transactions | Read replicas |
| Query | Point lookups | Aggregations |
| Storage | Row-oriented | Columnar |

**Why OLAP needed:**
```
OLTP Query: SELECT * FROM orders WHERE id=123
OLAP Query: SELECT city, AVG(amount) FROM orders GROUP BY city
→ OLTP chokes on GROUP BY 1B rows
```

## 2. Real-World Example - Flipkart

```
Flipkart (1M orders/hour):
OLTP: MySQL Aurora (order writes)
OLAP: Redshift (sales analytics)
Why separate? Monthly report = 100TB scan
MySQL would timeout/crash
```

## 3. Practical Scenario

**Amazon Seller Dashboard:**
```
OLTP: Orders table (RDS)
  INSERT order (1ms)
  UPDATE status (2ms)

OLAP: Sales fact table (Redshift)
  SELECT SUM(amount) BY seller (30s → 3s columnar)

BI Tool reads OLAP only
```

## 4. Common Mistakes

| Mistake | Impact | Fix |
|---------|--------|-----|
| Analytics on OLTP | DB crash | Separate OLAP |
| No read replicas | Query timeouts | Streaming CDC |
| Row storage for analytics | 100x slower | Columnar (Parquet) |
| Complex reports on OLTP | Billing explosion | Materialized views |

## 5. Performance Tips

```
OLTP → OLAP Pipeline:
Kafka CDC → S3 → Spark → Redshift

🏆 Query Speed:
Row: SELECT * FROM 1B = 5min
Columnar: AVG on 1B = 10s
```

## 6. 🔥 Interview Questions

### Amazon L5
**Q1: Why shouldn't analytics run on OLTP DB?**
```
A: 1. Blocks production writes 2. Index scans explode
   3. Normalized schema = 20 JOINs 4. Cost 100x
   
Ex: Amazon RDS analytics → Redshift Spectrum
```

**Q2 Follow-up: How to sync OLTP→OLAP?**
```
A: Debezium CDC → Kafka → S3 → Glue → Redshift
   Exactly-once + schema evolution
```

### Uber L4
**Q3: Design Flipkart analytics system**
```
A: Aurora (OLTP) → DMS CDC → S3 → Athena (OLAP)
   Cost: $0.02/query vs $5 RDS scan
```

**Q4: Normalized vs star schema?**
```
A: OLTP normalized (no redundancy)
   OLAP star (fewer JOINs, faster queries)
```

### Netflix Scenario
**Q5: 1PB viewing data analytics slow. Fix?**
```
A: Migrate to Snowflake (separation of storage/compute)
   Columnar + auto-scaling = 50x speedup
```

**Q6: ACID vs analytics tradeoff?**
```
A: OLTP needs ACID, OLAP sacrifices for speed
   Use Delta/Iceberg for ACID OLAP
```

---

**⚡ Pro Tip:** Never run BI queries on OLTP. $10K lesson learned.
