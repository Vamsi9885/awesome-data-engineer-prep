# 🏭 Data Warehouse vs Data Lake

## 1. Concept Explanation

**The Evolution:**
```
DW: Structured, governed (Snowflake)
Lake: Raw, cheap (S3) 
Lakehouse: Best of both (Delta/Iceberg)

Reality: 90% companies have both
```

**Comparison:**
| Aspect | Data Warehouse | Data Lake | Lakehouse |
|--------|----------------|-----------|-----------|
| Data Types | Structured | Raw (JSON/logs) | All |
| Schema | On-write | On-read | On-read + enforcement |
| Cost | $$$$$ | $ | $$ |
| Governance | ACID | Chaos | ACID + governance |
| Use Case | BI reports | ML + ad-hoc | Everything |

**Lakehouse = DW + Lake:**
```
Delta Lake: ACID on S3
Iceberg: Schema evolution
Hudi: Streaming upserts
```

## 2. Real-World Example - Netflix

```
Netflix (2PB/day):
Lake: S3 raw viewing events
DW: Redshift aggregated metrics
Lakehouse: Delta on S3 (ML features)

Why lake? ML needs raw pixel-level data
```

## 3. Practical Scenario

**Swiggy Order Intelligence:**
```
Lake: S3 raw orders (Parquet)
DW: Snowflake BI tables
Pipeline: Spark → Bronze Lake → Silver DW
Cost: Lake $100/TB, DW $3000/TB
```

## 4. Common Mistakes

| Mistake | Impact | Fix |
|---------|--------|-----|
| Lake = Data swamp | Unusable data | Schema enforcement |
| DW for ML | 100x cost | Lake for raw |
| No governance | Compliance fail | Unity Catalog |
| Manual catalogs | Metadata hell | Glue/Collibra |

## 5. Performance Tips

```
🏆 Storage Tier List:
S-Tier: Lakehouse (Delta/Iceberg)
A-Tier: Lake + Catalog (Athena)
B-Tier: DW (Snowflake)
F-Tier: Lake swamp

Query Cost: Lake $0.02/TB → DW $5/TB
```

## 6. 🔥 Interview Questions

### Amazon L5
**Q1: Snowflake vs Data Lake?**
```
A: Snowflake: Structured BI ($ expensive)
   Lake: Raw ML + ad-hoc ($ cheap)
   Use both: Medallion architecture
```

**Q2 Follow-up: Lakehouse advantages?**
```
A: ACID transactions on S3
   Schema evolution + time travel
   80% cost savings vs Snowflake
```

### Uber L4
**Q3: Design 10PB ride data storage**
```
A: S3 Lake (Bronze raw) + Iceberg Lakehouse (Silver/Gold)
   Trino queries across layers
```

**Q4: Data swamp. How to fix?**
```
A: 1. Schema registry 2. Data contracts
   3. Quality gates 4. Lineage tracking
```

### Snowflake Scenario
**Q5: Migrate 1PB from Snowflake to Lake. Risks?**
```
A: Lose ACID → Use Delta
   Governance → Unity Catalog
   Performance → Z-order + compaction
```

**Q6: When NOT to use Data Lake?**
```
A: Regulated data (healthcare) needs governance
   Small datasets (<1TB) → DW simpler
```

---

**⚡ Pro Tip:** Lakehouse is future. Learn Delta/Iceberg now.
