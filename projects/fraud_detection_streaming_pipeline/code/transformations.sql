WITH base_txn AS (
  SELECT
    transaction_id,
    card_hash,
    merchant_id,
    amount,
    currency,
    country,
    event_ts,
    device_id,
    ip_address
  FROM bronze.card_transactions
),

dedup AS (
  SELECT *
  FROM (
    SELECT
      *,
      ROW_NUMBER() OVER (
        PARTITION BY transaction_id
        ORDER BY event_ts DESC
      ) AS rn
    FROM base_txn
  ) t
  WHERE rn = 1
),

feature_enriched AS (
  SELECT
    transaction_id,
    card_hash,
    merchant_id,
    amount,
    country,
    event_ts,
    COUNT(*) OVER (
      PARTITION BY card_hash
      ORDER BY event_ts
      RANGE BETWEEN INTERVAL 5 MINUTES PRECEDING AND CURRENT ROW
    ) AS card_velocity_5m,
    SHA2(CONCAT(COALESCE(device_id, ''), '|', COALESCE(ip_address, '')), 256) AS device_ip_fingerprint
  FROM dedup
),

scored AS (
  SELECT
    *,
    CASE
      WHEN amount > 5000 THEN 40 ELSE 0
    END
    + CASE
      WHEN card_velocity_5m > 5 THEN 35 ELSE 0
    END AS rule_score
  FROM feature_enriched
)

SELECT * FROM scored;
