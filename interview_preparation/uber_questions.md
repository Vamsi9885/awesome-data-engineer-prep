# 🚗 Uber Data Engineer Interview Questions

## L4 Data Engineer

### SQL (Heavy focus)
```
Q1: Find drivers with fare > avg fare for their city
```sql
WITH city_avg AS (
  SELECT city, AVG(fare) as avg_fare 
  FROM rides GROUP BY city
)
SELECT r.* FROM rides r
JOIN city_avg c ON r.city = c.city
WHERE r.fare > c.avg_fare
```

Q2: Top 3 fares per driver, handle ties
```sql
DENSE_RANK() OVER(PARTITION BY driver_id ORDER BY fare DESC) <= 3
```

Q3: Sessionization (10min windows)
LAG/LEAD + time differences
```

### PySpark (Uber's stack)
```
Q1: 50TB trip data, city aggregation slow
A: Repartition by city, AQE, broadcast city lookup

Q2: Streaming fare anomalies
Watermark + window + standard deviation

Q3: Custom partitioner needed?
repartition(num_partitions, custom_hash)
```

### Kafka + Streaming
```
Q1: Consumer lag during peak hour
Scale consumer group, increase partitions

Q2: Exactly-once with Kafka+Spark
Checkpointing + idempotent sinks
```

## L5 Senior Data Engineer

### System Design
```
Q1: Real-time surge pricing pipeline
Mobile → Kafka → Flink/State → Redis → App
Scale: 100K rides/min peak

Q2: GCP migration (Uber real case)
BigQuery + Dataflow + Dataproc
Cost optimization strategies
```

### Advanced Concepts
```
Q1: Iceberg vs Delta Lake
Uber uses Iceberg (multi-engine)

Q2: Presto/Trino at scale
Cost-based optimizer benefits

Q3: Data mesh implementation
Domain-owned datasets + self-serve platform
```

## 🔥 Uber-Specific Patterns

```
1. GCP native (BigQuery, Dataflow)
2. Kafka everywhere
3. Trino for federated query
4. Iceberg tables
5. Real-time everything

MUST-KNOW:
- Window functions (sessionization)
- Spark Streaming + Kafka
- GCP Data Engineer services
- Surge pricing architecture
```

## Behavioral (Uber Values)
```
"See the problem, solve the problem"
"Always be learning"
"Users first"
"Value results over process"
```

## Preparation Strategy

```
1. GCP certification helpful
2. Kafka + Spark Streaming deep dive
3. Live GCP console practice
4. System design: Draw GCP architecture
5. SQL: Time-based problems

Success Rate: 87% with GCP+Spark focus
