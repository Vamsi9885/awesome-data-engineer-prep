WITH orders_base AS (
  SELECT
    order_id,
    customer_id,
    product_id,
    country,
    channel,
    CAST(order_ts AS TIMESTAMP) AS order_ts,
    DATE(CAST(order_ts AS TIMESTAMP)) AS event_date,
    quantity,
    unit_price,
    COALESCE(discount_amount, 0.0) AS discount_amount,
    updated_at
  FROM bronze.orders_incremental
),

deduped AS (
  SELECT *
  FROM (
    SELECT
      *,
      ROW_NUMBER() OVER (
        PARTITION BY order_id
        ORDER BY updated_at DESC
      ) AS rn
    FROM orders_base
  ) x
  WHERE rn = 1
),

silver_orders AS (
  SELECT
    order_id,
    customer_id,
    product_id,
    country,
    channel,
    event_date,
    quantity,
    unit_price,
    discount_amount,
    (quantity * unit_price) AS gross_amount,
    (quantity * unit_price) - discount_amount AS net_amount
  FROM deduped
)

SELECT * FROM silver_orders;
