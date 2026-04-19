-- Real-Time Ride Tracking SQL

-- 1) Silver deduped events
CREATE OR REPLACE TEMP VIEW v_ride_events_deduped AS
SELECT *
FROM (
  SELECT
    event_id,
    ride_id,
    driver_id,
    rider_id,
    city_id,
    event_type,
    event_ts,
    ingest_ts,
    lat,
    lon,
    event_version,
    ROW_NUMBER() OVER (
      PARTITION BY event_id
      ORDER BY ingest_ts DESC
    ) AS rn
  FROM rides.bronze_events
)
WHERE rn = 1;

MERGE INTO rides.silver_events t
USING v_ride_events_deduped s
ON t.event_id = s.event_id
WHEN MATCHED THEN UPDATE SET
  t.ride_id = s.ride_id,
  t.driver_id = s.driver_id,
  t.rider_id = s.rider_id,
  t.city_id = s.city_id,
  t.event_type = s.event_type,
  t.event_ts = s.event_ts,
  t.ingest_ts = s.ingest_ts,
  t.lat = s.lat,
  t.lon = s.lon,
  t.event_version = s.event_version
WHEN NOT MATCHED THEN INSERT (
  event_id, ride_id, driver_id, rider_id, city_id,
  event_type, event_ts, ingest_ts, lat, lon, event_version
) VALUES (
  s.event_id, s.ride_id, s.driver_id, s.rider_id, s.city_id,
  s.event_type, s.event_ts, s.ingest_ts, s.lat, s.lon, s.event_version
);

-- 2) Gold active rides by 1-minute windows
CREATE OR REPLACE TABLE rides.gold_active_rides_1min
USING DELTA
PARTITIONED BY (ds)
AS
WITH latest_status AS (
  SELECT
    ride_id,
    city_id,
    event_type,
    event_ts,
    DATE(event_ts) AS ds,
    ROW_NUMBER() OVER (PARTITION BY ride_id ORDER BY event_ts DESC, ingest_ts DESC) AS rn
  FROM rides.silver_events
)
SELECT
  ds,
  city_id,
  COUNT(*) AS active_rides
FROM latest_status
WHERE rn = 1
  AND event_type IN ('ride_requested','driver_assigned','trip_started')
GROUP BY ds, city_id;

-- 3) Gold cancellation rate by 5-min bucket
CREATE OR REPLACE TABLE rides.gold_cancellation_rate_5min
USING DELTA
PARTITIONED BY (ds)
AS
SELECT
  DATE(event_ts) AS ds,
  city_id,
  window_start,
  window_end,
  SUM(CASE WHEN event_type = 'trip_canceled' THEN 1 ELSE 0 END) AS canceled_cnt,
  SUM(CASE WHEN event_type = 'ride_requested' THEN 1 ELSE 0 END) AS requested_cnt,
  CASE
    WHEN SUM(CASE WHEN event_type = 'ride_requested' THEN 1 ELSE 0 END) = 0 THEN 0
    ELSE SUM(CASE WHEN event_type = 'trip_canceled' THEN 1 ELSE 0 END) * 1.0
         / SUM(CASE WHEN event_type = 'ride_requested' THEN 1 ELSE 0 END)
  END AS cancellation_rate
FROM (
  SELECT
    city_id,
    event_type,
    event_ts,
    date_trunc('minute', event_ts) AS window_start,
    date_trunc('minute', event_ts) + INTERVAL 5 MINUTES AS window_end
  FROM rides.silver_events
) x
GROUP BY DATE(event_ts), city_id, window_start, window_end;
