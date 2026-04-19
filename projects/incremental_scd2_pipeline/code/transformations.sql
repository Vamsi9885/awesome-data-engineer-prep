-- incremental_scd2_pipeline/code/transformations.sql

WITH source_events AS (
    SELECT
        customer_id,
        customer_name,
        tier,
        city,
        risk_score,
        segment,
        source_system,
        source_seq_id,
        CAST(event_ts AS TIMESTAMP) AS event_ts,
        ingestion_ts
    FROM bronze.customer_cdc_events
),

deduped AS (
    SELECT *
    FROM (
        SELECT
            *,
            ROW_NUMBER() OVER (
                PARTITION BY customer_id, event_ts, source_seq_id
                ORDER BY ingestion_ts DESC
            ) AS rn
        FROM source_events
    ) t
    WHERE rn = 1
),

hashed AS (
    SELECT
        *,
        SHA2(
            CONCAT_WS('||',
                COALESCE(customer_name, ''),
                COALESCE(tier, ''),
                COALESCE(city, ''),
                COALESCE(CAST(risk_score AS STRING), ''),
                COALESCE(segment, '')
            ),
            256
        ) AS record_hash,
        event_ts AS effective_start_ts
    FROM deduped
)

SELECT
    customer_id,
    customer_name,
    tier,
    city,
    risk_score,
    segment,
    source_system,
    source_seq_id,
    record_hash,
    effective_start_ts,
    TIMESTAMP('9999-12-31 00:00:00') AS effective_end_ts,
    TRUE AS is_current,
    ingestion_ts
FROM hashed;
