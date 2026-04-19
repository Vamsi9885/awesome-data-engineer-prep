# 🛠️ Data Engineering Basics

## 1. Concept Explanation

**Data Engineering ≠ Data Science**
```
Data Engineers: Build pipelines (99% infrastructure)
Data Scientists: Build models (1% infrastructure)

DE Reality: 1TB/day pipeline failure = $1M revenue loss
```

**Core Responsibilities:**
| Area | What You Do | Tools |
|------|-------------|-------|
| Ingestion | Kafka/S3 from sources | Kafka, Kinesis |
| Transformation | Clean/aggregate | Spark, Airflow |
| Storage | Optimize formats | Parquet, Delta |
| Serving | Low-latency queries | Athena, Trino |
| Monitoring | Pipeline health | Prometheus, Datadog |

**End-to-End Architecture:**
```
Sources → Ingestion (Kafka) → Bronze (Raw S3) 
→ Silver (Cleaned Parquet) → Gold (Aggregated)
→ BI Tools (Tableau) / ML (SageMaker)
```

**Batch vs Streaming:**
| Batch | Streaming |
|-------|-----------|
| Hourly/daily | Real-time |
| Spark/Airflow | Flink/Kafka Streams |
| Higher throughput | Lower latency |

**ETL vs ELT:**
| ETL | ELT |
|----|----|
| Extract→Transform→Load | Extract→Load→Transform |
| Rigid schema | Schema-on-read |
| On-prem (Informatica) | Cloud (Spark/DBT) |

## 2. Real-World Example - Uber Ride Pipeline

```
Uber (50M rides/day):
1. Kafka: Raw GPS events (TB/hour)
2. Flink: Real-time surge pricing
3. Bronze S3: Raw Parquet (1PB)
4. Silver: Cleaned + enriched
5. Gold: Aggregated for analytics
6. Presto: Ad-hoc queries (<5s)
```

## 3. Practical Scenario

**Production Day-in-Life (Amazon L5 DE):**
```
6AM: Airflow DAGs trigger
8AM: Spark jobs process 10TB
10AM: Data quality checks pass
12PM: Gold tables updated
2PM: Tableau dashboards refresh
4PM: ML models retrain
6PM: Monitor SLAs (99.9% uptime)
```

## 4. Common Mistakes

| Mistake | Impact | Fix |
|---------|--------|-----|
| No idempotency | Duplicate data | Unique keys + upsert |
| Single point failure | Pipeline down | Multi-AZ + retries |
| No monitoring | Silent failures | Alerts + dashboards |
| Over-engineering | 6-month delivery | MVP first |

## 5. Performance Tips

```
🏆 Pipeline Tier List:
S-Tier: Idempotent + Monitored + Partitioned
A-Tier: ELT + Serverless (Glue)
F-Tier: Custom ETL scripts

Cost Rule: $1 compute = $0.10 storage
```

## 6. 🔥 Interview Questions

### Amazon L4
**Q1: Design Uber's ride data pipeline (1B events/day)**
```
A: Kafka→Flink (real-time)→S3 Bronze→Spark Silver→Presto Gold
   Partition: date,city. Idempotent: ride_id upsert
```

**Q2 Follow-up: ETL vs ELT for this?**
```
A: ELT - Raw first, transform later. Schema evolution friendly
```

### Uber L5
**Q3: Batch vs streaming - when streaming?**
```
A: Latency <5min (surge pricing, fraud)
   Batch: Daily reports (cheaper)
```

**Q4: Pipeline failed midnight. How to debug?**
```
A: 1. Check Airflow logs 2. Spark UI 3. Data quality metrics
   4. Rollback to last good version
```

### Netflix Scenario
**Q5: 1PB viewing data. Architecture?**
```
A: Kinesis→S3 Bronze (hourly)→Spark daily→Iceberg Gold
   Cost: $0.02/query via Trino
```

**Q6: Why separate DE from DS teams?**
```
A: DE owns infra (99% time). DS owns models (1% infra)
   Wrong: DS building pipelines = delayed ML
```

---

**⚡ Pro Tip:** Always design for failure. 99% of production issues = retry logic missing.
