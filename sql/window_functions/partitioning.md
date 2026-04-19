# 🧠 PARTITION BY & FRAME CLAUSES + SESSIONIZATION

## 1. Problem Statement
Group user activity into sessions using inactivity threshold (30 mins), and compute session IDs.

## 2. Sample Data
| user_id | event_time           | event_type |
|--------:|----------------------|------------|
| 1       | 2024-02-01 10:00:00  | view       |
| 1       | 2024-02-01 10:10:00  | click      |
| 1       | 2024-02-01 11:00:00  | add_to_cart|
| 1       | 2024-02-01 11:20:00  | purchase   |
| 2       | 2024-02-01 09:00:00  | login      |
| 2       | 2024-02-01 09:50:00  | view       |

## 3. SQL Query
```sql
WITH base AS (
  SELECT
      user_id,
      event_time,
      event_type,
      LAG(event_time) OVER (
        PARTITION BY user_id
        ORDER BY event_time
      ) AS prev_event_time
  FROM user_activity
),
flags AS (
  SELECT *,
         CASE
           WHEN prev_event_time IS NULL THEN 1
           WHEN event_time - prev_event_time > INTERVAL '30 minute' THEN 1
           ELSE 0
         END AS new_session_flag
  FROM base
),
sessionized AS (
  SELECT *,
         SUM(new_session_flag) OVER (
           PARTITION BY user_id
           ORDER BY event_time
           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
         ) AS session_id
  FROM flags
)
SELECT user_id, event_time, event_type, session_id
FROM sessionized
ORDER BY user_id, event_time;
```

## 4. Explanation
`PARTITION BY user_id` isolates each user timeline; LAG computes previous event; cumulative sum of session-start flags assigns stable session ids.

## 5. Variations / Edge Cases
- Different inactivity threshold by platform.
- Merge very short sessions.
- Handle out-of-order late events with watermarking in streaming systems.

## 6. Performance Considerations
- Index `(user_id, event_time)`.
- Partition activity table by event_date.
- Apply date filters before windows.
- Keep sessionization in incremental models for large data.

## 7. 🔥 Interview Questions
**Basic:** Why use PARTITION BY?  
**Advanced:** sessionization with configurable thresholds.  
**Product scenario:** web analytics session metrics and conversion per session.  
**Follow-up:** late events, timezone, streaming-vs-batch consistency.

## Common Mistakes
- Not sorting events within partition.
- Global sessionization without user partition.
- Wrong threshold units (minutes vs seconds).
