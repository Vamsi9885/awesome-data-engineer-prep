# 💰 Amazon Data Engineer Interview Questions

## L4 Data Engineer (80% of openings)

### SQL (3/4 rounds)
```
Q1: Second highest fare per driver
```sql
SELECT * FROM (
  SELECT *, DENSE_RANK() OVER(PARTITION BY driver_id ORDER BY fare DESC) rnk
  FROM rides
) WHERE rnk = 2
```

Q2: Running total revenue (window function)
```sql
SUM(revenue) OVER(PARTITION BY customer ORDER BY order_date 
                  ROWS UNBOUNDED PRECEDING)
```

Q3: Find duplicate ride_ids
```sql
HAVING COUNT(*) > 1 FROM rides GROUP BY ride_id
```
```

### PySpark (2/4 rounds)
```
Q1: Optimize slow 10TB join
A: broadcast(small_df), repartition(), AQE

Q2: Handle skewed keys
A: salting (key + random()), repartition(num_partitions)

Q3: OOM during groupBy
A: coalesce(), increase shuffle partitions
```

### System Design (1 round)
```
Q1: Design Amazon order analytics pipeline (1B orders/day)
Raw: S3 → Spark EMR → Redshift → QuickSight
Cost: $3/TB optimized

Q2: Streaming ride pricing
Kinesis → Flink → DynamoDB (cache) → S3
```

## L5 Senior Data Engineer

### Advanced SQL
```
Q1: Median fare per city (no built-in)
```sql
SELECT city, PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY fare) 
FROM rides GROUP BY city
```

Q2: Complex cohort analysis
Window + self-join pattern
```

### Architecture Deep Dive
```
Q1: Handle 10TB daily with 99.99% uptime
- Multi-region S3
- Airflow + retries
- DLQ for failures
- Monitoring stack

Q2: Data quality framework
- Great Expectations + dbt tests
- Anomaly detection
- SLAs per pipeline
```

### Behavioral (Leadership Principles)
```
Customer Obsession: "Fixed dashboard latency from 5min→10s"
Ownership: "Built self-service analytics platform"
Dive Deep: "Analyzed why 3% orders had NULL customer_id"
```

## 🔥 Amazon-Specific Patterns

```
1. Always partition by date
2. Parquet + Snappy compression
3. EMR spot instances (70% savings)
4. Athena partition projection
5. Glue schema registry

MOST ASKED (90% hit rate):
- Window functions (RANK, running totals)
- Spark performance tuning
- Star schema design
- Pipeline failure recovery
```

## Preparation Tips

```
1. Practice LIVE coding (CoderPad)
2. Explain your thought process
3. Start simple → Optimize
4. Ask clarifying questions
5. Big-O complexity awareness

Success Rate: 85% with this prep
