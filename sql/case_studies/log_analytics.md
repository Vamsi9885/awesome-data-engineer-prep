# 🧪 CASE STUDY - Log Analytics (Netflix/System Analytics)

## Scenario
Analyze application event logs for reliability and user flow insights.

## Sample Data
| user_id | event_time           | event_name   | page      |
|--------:|----------------------|--------------|-----------|
| 1       | 2024-02-01 10:00:00  | app_open     | home      |
| 1       | 2024-02-01 10:01:00  | search       | search    |
| 1       | 2024-02-01 10:03:00  | play_start   | player    |
| 2       | 2024-02-01 10:00:00  | app_open     | home      |
| 2       | 2024-02-01 10:04:00  | error        | checkout  |
| 2       | 2024-02-01 10:10:00  | retry        | checkout  |

## Tasks (6)
1. DAU  
2. Error rate per day  
3. Latest event per user  
4. Sessionization from inactivity gap  
5. Funnel conversion (app_open -> play_start)  
6. Duplicate event detection

## Solutions
```sql
-- 1 DAU
SELECT DATE(event_time) d, COUNT(DISTINCT user_id) dau
FROM logs
GROUP BY DATE(event_time);
```

```sql
-- 2 Error rate
SELECT DATE(event_time) d,
  100.0*SUM(CASE WHEN event_name='error' THEN 1 ELSE 0 END)/COUNT(*) AS error_rate
FROM logs
GROUP BY DATE(event_time);
```

```sql
-- 3 latest record per user
SELECT user_id, event_time, event_name
FROM (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY event_time DESC) rn
  FROM logs
) t
WHERE rn=1;
```

```sql
-- 4 sessionization skeleton (30 min threshold)
-- same lag + cumulative sum approach
```

```sql
-- 5 funnel stage counts
SELECT
  COUNT(DISTINCT CASE WHEN event_name='app_open' THEN user_id END) open_users,
  COUNT(DISTINCT CASE WHEN event_name='play_start' THEN user_id END) play_users
FROM logs;
```

```sql
-- 6 dedup
SELECT *
FROM (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY user_id,event_time,event_name,page ORDER BY event_time) rn
  FROM logs
) t
WHERE rn=1;
```

## Variations / Edge Cases
- Bot filtering.
- Event schema evolution.
- Delayed ingestion.

## Performance Considerations
- Partition by event_date.
- Index `(event_name, event_time, user_id)`.
- Use approximate distinct for very large cardinality when acceptable.

## 🔥 Interview Questions
**Basic:** DAU computation.  
**Advanced:** robust funnel across late events and retries.  
**Product scenario:** sudden error spike diagnosis.  
**Follow-up:** logging quality, idempotent ingestion, dedup strategy.

## Common Mistakes
- Counting raw events instead of users in funnel.
- Ignoring timezone normalization.
- Dedup without deterministic key.
