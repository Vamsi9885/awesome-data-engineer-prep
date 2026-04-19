# 🔄 Apache Airflow Mastery

## 1. Concept Explanation

**Airflow = Production Pipeline Orchestrator**

```
Cron: Simple, no retries
Airflow: DAGs, retries, parallelism, monitoring, SLA

90% of DE jobs require orchestration
```

**Core Concepts:**
- **DAG** = Pipeline definition
- **Tasks** = Pipeline steps
- **Operators** = Pre-built actions
- **XCom** = Task communication

## 2. Real-World Example - Uber ETL Pipeline

```
Uber Daily Pipeline:
Extract (S3) → Transform (Spark EMR) → Load (Redshift)
3hr runtime, 99.9% success rate
```

## 3. Code Examples

### Production DAG Template
```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.operators.emr import EmrAddStepsOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': True,
    'sla': timedelta(hours=2)
}

dag = DAG(
    'uber_daily_etl',
    default_args=default_args,
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['etl', 'uber']
)

# Extract
extract_task = PythonOperator(
    task_id='extract_orders',
    python_callable=extract_orders_s3,
    dag=dag
)

# Transform (EMR Spark)
spark_step = EmrAddStepsOperator(
    task_id='transform_spark',
    job_flow_id='{{ var.value.emr_cluster_id }}',
    steps=[{
        'Name': 'uber_etl',
        'ActionOnFailure': 'CONTINUE',
        'HadoopJarStep': {
            'Jar': 'command-runner.jar',
            'Args': ['spark-submit', 's3://uber-scripts/etl.py']
        }
    }],
    dag=dag
)

# Load
load_task = PythonOperator(
    task_id='load_redshift',
    python_callable=load_to_redshift,
    dag=dag
)

extract_task >> spark_step >> load_task
```

### Dynamic Task Generation
```python
# Process multiple tables
table_list = ['orders', 'customers', 'products']

for table in table_list:
    transform_task = SparkSubmitOperator(
        task_id=f'transform_{table}',
        application='s3://scripts/transform.py',
        conf={'spark.sql.shuffle.partitions': '400'},
        dag=dag
    )
    # Dynamic dependencies...
```

## 4. Real-Time Production Scenario

**Flipkart Black Friday Pipeline (10M orders/hour):**

```
DAG: flipkart_peak_etl
Parallelism: 50 Spark jobs
Retry: 5x with exponential backoff
SLA: 4hr daily window
Monitoring: Slack + PagerDuty

Success rate: 99.97%
```

## 5. Common Mistakes

| Mistake | Symptom | Fix |
|---------|---------|-----|
| No retries | 1 failure = pipeline down | retries=3 |
| Sequential tasks | 10hr runtime | parallelism |
| No SLAs | No accountability | sla=timedelta(hours=2) |
| Hardcoded paths | Env-specific | Variables/Airflow Variables |

## 6. Production Checklist

```
🏆 Airflow Production Config:

Executor: CeleryExecutor (not Sequential)
Workers: 50+ 
Database: PostgreSQL (not SQLite)
Security: RBAC + Kerberos

Monitoring:
- DAG runs (Graph view)
- Task duration trends
- Pool exhaustion
- XCom size limits
```

## 7. 🔥 Interview Questions

### Amazon L5
**Q1: DAG failed mid-way. Recovery?**
```
A: Clear downstream tasks → Resume from failure
airflow tasks clear -s 2024-01-15 dag_id downstream_task
```

**Q2: Dynamic DAGs for 100 tables?**
```
PythonOperator with loop → TaskGroup (Airflow 2.0)
Macro: {{ ds }} for dates
```

### Uber L4
**Q3: Spark job in Airflow. Best operator?**
```
EmrAddStepsOperator (AWS)
DatabricksSubmitRunOperator (Azure/GCP)
SparkSubmitOperator (vanilla)
```

**Q4: Branching logic?**
```
BranchPythonOperator → Multiple downstream paths
ShortCircuitOperator → Early exit
```

### Flipkart Orchestration
**Q5: 1000 DAGs management.**
```
A: 
1. Dynamic DAG generation
2. TaskGroups for organization
3. Pools for resource control
4. Variables for config
```

**Q6: Backfill strategy.**
```
airflow dags backfill -s 2024-01-01 -e 2024-01-31 dag_id
--rerun-failed-tasks
```

---

**🎯 Pro Tip:** Airflow UI = Production dashboard. Live monitoring > cron emails
```
Graph view → Gantt → Code → Grid = Complete picture
