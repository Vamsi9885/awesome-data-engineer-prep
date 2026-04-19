WITH base AS (
  SELECT
    CAST(timestamp AS TIMESTAMP) AS event_ts,
    DATE(CAST(timestamp AS TIMESTAMP)) AS event_date,
    service_name,
    env,
    region,
    severity,
    message,
    trace_id,
    span_id,
    event_id,
    ingestion_ts
  FROM bronze.raw_logs
),

filtered AS (
  SELECT *
  FROM base
  WHERE event_ts IS NOT NULL
    AND service_name IS NOT NULL
    AND UPPER(severity) IN ('DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL')
),

deduped AS (
  SELECT *
  FROM (
    SELECT
      *,
      ROW_NUMBER() OVER (
        PARTITION BY event_id
        ORDER BY ingestion_ts DESC
      ) AS rn
    FROM filtered
  ) x
  WHERE rn = 1
),

enriched AS (
  SELECT
    event_ts,
    event_date,
    service_name,
    env,
    region,
    UPPER(severity) AS severity,
    message,
    trace_id,
    span_id,
    event_id,
    SHA2(COALESCE(message, ''), 256) AS message_hash
  FROM deduped
)

SELECT * FROM enriched;
