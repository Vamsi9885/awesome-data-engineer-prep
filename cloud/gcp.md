# ☁️ GCP for Data Engineers

## 1. Concept Explanation

**GCP = Fastest growing (Uber, Spotify)**

```
GCP Mapping:
BigQuery → Athena/Redshift
Dataproc → EMR  
Dataflow → Glue Streaming
Pub/Sub → Kinesis
Cloud Storage → S3
```

**GCP Superpowers:**
- BigQuery ML (SQL + ML)
- Dataflow (Flink runner)
- Serverless everything

## 2. Real-World Example - Uber Data Platform

```
Uber's GCP Migration:
S3 → GCS (same API!)
EMR → Dataproc
Redshift → BigQuery (10x faster)

Result: 70% cost reduction
```

## 3. Code Examples

### BigQuery Production Queries
```sql
-- Uber: Driver leaderboard (real query)
WITH ranked_drivers AS (
  SELECT 
    driver_id,
    SUM(fare) as total_fare,
    COUNT(*) as trips,
    ROW_NUMBER() OVER (ORDER BY SUM(fare) DESC) as rank
  FROM `uber_dataset.trips`
  WHERE DATE(_PARTITIONTIME) = '2024-01-15'
  GROUP BY driver_id
)
SELECT * FROM ranked_drivers WHERE rank <= 100;
```

### Dataflow Pipeline (Python)
```python
import apache_beam as beam

# Uber trip processing
with beam.Pipeline() as pipeline:
    (pipeline 
     | 'ReadFromPubSub' >> beam.io.ReadFromPubSub(subscription='projects/uber/topics/trips')
     | 'ParseJSON' >> beam.Map(json.loads)
     | 'FilterValid' >> beam.Filter(lambda x: x['fare'] > 0)
     | 'WriteParquet' >> beam.io.WriteToParquet('gs://uber-curated/trips/'))
```

### Dataproc Spark Submit
```bash
gcloud dataproc jobs submit pyspark gs://uber-scripts/process_trips.py \
    --cluster=uber-cluster \
    --region=us-central1 \
    --properties=spark.sql.shuffle.partitions=400
```

## 4. Real-Time Production Scenario

**Swiggy GCP Streaming (Real-time ETA):**

```
Pub/Sub (orders) → Dataflow (Beam) → 
BigQuery (streaming insert) → Looker

Latency: Order to dashboard < 5s
Cost: $0.02/order processed
Scale: 100K orders/hour peak
```

## 5. Common Mistakes

| Service | Mistake | Fix |
|---------|---------|-----|
| BigQuery | No clustering | CLUSTER BY (city, date) |
| Dataflow | Fixed workers | Autoscaling |
| GCS | No lifecycle | Intelligent tiering |

## 6. GCP Cost Framework

```
🏆 GCP Pricing Guide:

BigQuery: $5/TB scanned (slot-based)
Dataproc: $0.01/core-min (preemptible)
Dataflow: $0.01/vCPU-hour
GCS: $0.02/GB (hot storage)

Optimization:
1. BigQuery clustering (90% scan reduction)
2. Dataproc preemptible (80% savings)
3. Partitioned tables everywhere
```

## 7. 🔥 Interview Questions

### Uber L5 (GCP Heavy)
**Q1: BigQuery slow query (1TB table).**
```sql
-- Fix:
SELECT * FROM `project.dataset.table`
WHERE DATE(_PARTITIONTIME) = '2024-01-15'  -- Partition
  AND city = 'blr'                          -- Cluster
```

**Q2: BigQuery vs Snowflake?**
```
BigQuery: Serverless, ML built-in
Snowflake: Multi-cloud, Time Travel
```

### Spotify L4
**Q3: Dataflow backpressure.**
```
A: 
1. Autoscaling (100-1000 workers)
2. Windowing + watermark
3. Multiple pipelines
```

**Q4: GCS partitioning strategy?**
```
gs://bucket/dt=2024-01-15/city=blr/
BigQuery external table auto-discovers
```

### Flipkart Multi-Cloud
**Q5: Migrate S3→GCS pipeline.**
```
A: 
1. gsutil cp -r s3://... gs://...
2. Update Spark paths
3. Same Parquet schema
4. BigQuery external tables
```

**Q6: BigQuery ML use case?**
```sql
CREATE MODEL `uber.churn_model`
OPTIONS(model_type='logistic_reg') AS
SELECT * FROM `uber.features` 
EXCEPT (churn);
```

---

**⚡ Pro Tip:** GCP Console → BigQuery → Query History = Learn from production queries
```
BigQuery slots = your compute budget
