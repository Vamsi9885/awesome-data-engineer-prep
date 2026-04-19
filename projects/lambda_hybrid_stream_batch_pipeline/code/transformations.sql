WITH speed_metrics AS (
  SELECT
    window.start AS window_start,
    window.end AS window_end,
    events_per_minute
  FROM serving.kpi_speed
),

batch_metrics AS (
  SELECT
    event_date,
    daily_events
  FROM serving.kpi_batch
),

reconciled AS (
  SELECT
    s.window_start,
    s.window_end,
    s.events_per_minute,
    b.daily_events,
    CASE
      WHEN b.daily_events IS NULL THEN s.events_per_minute
      ELSE s.events_per_minute
    END AS unified_metric
  FROM speed_metrics s
  LEFT JOIN batch_metrics b
    ON DATE(s.window_start) = b.event_date
)

SELECT * FROM reconciled;
