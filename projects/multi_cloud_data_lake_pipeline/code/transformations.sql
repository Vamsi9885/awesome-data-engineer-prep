-- Multi-Cloud Data Lake Pipeline SQL Transformations

-- 1) Silver canonical orders (dedupe + standardization)
CREATE OR REPLACE TEMP VIEW v_orders_canonical AS
SELECT
    order_id,
    customer_id,
    UPPER(country_code) AS country_code,
    TO_TIMESTAMP(order_ts) AS order_ts_utc,
    TO_DATE(TO_TIMESTAMP(order_ts)) AS event_date,
    currency_code,
    CASE
        WHEN currency_code = 'USD' THEN order_amount
        WHEN currency_code = 'EUR' THEN order_amount * 1.08
        WHEN currency_code = 'GBP' THEN order_amount * 1.26
        ELSE order_amount
    END AS order_amount_usd,
    source_cloud,
    source_path,
    ingest_ts,
    run_id,
    SHA2(CONCAT_WS('||',
        COALESCE(CAST(order_id AS STRING), ''),
        COALESCE(CAST(customer_id AS STRING), ''),
        COALESCE(CAST(order_ts AS STRING), ''),
        COALESCE(CAST(order_amount AS STRING), ''),
        COALESCE(CAST(currency_code AS STRING), '')
    ), 256) AS record_hash
FROM lakehouse.bronze_orders;

CREATE OR REPLACE TEMP VIEW v_orders_deduped AS
SELECT *
FROM (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY order_id
            ORDER BY order_ts_utc DESC, ingest_ts DESC
        ) AS rn
    FROM v_orders_canonical
)
WHERE rn = 1;

-- 2) Merge into silver
MERGE INTO lakehouse.silver_orders AS t
USING v_orders_deduped AS s
ON t.order_id = s.order_id
AND t.event_date = s.event_date
WHEN MATCHED AND t.record_hash <> s.record_hash THEN UPDATE SET
    t.customer_id = s.customer_id,
    t.country_code = s.country_code,
    t.order_ts_utc = s.order_ts_utc,
    t.currency_code = s.currency_code,
    t.order_amount_usd = s.order_amount_usd,
    t.source_cloud = s.source_cloud,
    t.source_path = s.source_path,
    t.ingest_ts = s.ingest_ts,
    t.run_id = s.run_id,
    t.record_hash = s.record_hash
WHEN NOT MATCHED THEN INSERT (
    order_id,
    customer_id,
    country_code,
    order_ts_utc,
    event_date,
    currency_code,
    order_amount_usd,
    source_cloud,
    source_path,
    ingest_ts,
    run_id,
    record_hash
) VALUES (
    s.order_id,
    s.customer_id,
    s.country_code,
    s.order_ts_utc,
    s.event_date,
    s.currency_code,
    s.order_amount_usd,
    s.source_cloud,
    s.source_path,
    s.ingest_ts,
    s.run_id,
    s.record_hash
);

-- 3) Build gold daily revenue mart
CREATE OR REPLACE TABLE lakehouse.gold_daily_revenue_country
USING DELTA
PARTITIONED BY (ds)
AS
SELECT
    event_date AS ds,
    country_code,
    COUNT(DISTINCT order_id) AS orders_cnt,
    SUM(order_amount_usd) AS gross_revenue_usd,
    APPROX_COUNT_DISTINCT(customer_id) AS buyers_cnt
FROM lakehouse.silver_orders
GROUP BY event_date, country_code;
