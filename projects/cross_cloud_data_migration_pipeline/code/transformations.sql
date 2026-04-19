WITH source_records AS (
  SELECT
    table_name,
    pk,
    op_type,
    op_ts,
    payload,
    ingestion_ts
  FROM bronze.source_cdc_events
),

ordered AS (
  SELECT *
  FROM (
    SELECT
      *,
      ROW_NUMBER() OVER (
        PARTITION BY table_name, pk, op_ts
        ORDER BY ingestion_ts DESC
      ) AS rn
    FROM source_records
  ) t
  WHERE rn = 1
),

validated AS (
  SELECT
    table_name,
    pk,
    op_type,
    CAST(op_ts AS TIMESTAMP) AS op_ts,
    payload,
    SHA2(COALESCE(CAST(payload AS STRING), ''), 256) AS payload_hash
  FROM ordered
)

SELECT * FROM validated;
