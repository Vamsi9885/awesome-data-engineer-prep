-- =====================================================
-- Azure Batch Pipeline Transformations (Delta SQL style)
-- =====================================================

-- 1) Bronze dedup for orders
WITH ranked_orders AS (
  SELECT
    *,
    ROW_NUMBER() OVER (
      PARTITION BY order_id
      ORDER BY updated_at DESC, ingest_ts DESC
    ) AS rn
  FROM bronze_orders
  WHERE ingest_date = '${run_date}'
)
SELECT
  order_id,
  customer_id,
  product_id,
  country,
  order_date,
  order_amount,
  updated_at
FROM ranked_orders
WHERE rn = 1;


-- 2) Silver quality-filtered payments
WITH payments_filtered AS (
  SELECT *
  FROM bronze_payments
  WHERE ingest_date = '${run_date}'
    AND payment_amount >= 0
    AND payment_id IS NOT NULL
    AND customer_id IS NOT NULL
),
dedup AS (
  SELECT
    *,
    ROW_NUMBER() OVER (
      PARTITION BY payment_id
      ORDER BY updated_at DESC
    ) AS rn
  FROM payments_filtered
)
SELECT
  payment_id,
  customer_id,
  country,
  payment_date,
  payment_amount,
  payment_method,
  updated_at
FROM dedup
WHERE rn = 1;


-- 3) Gold fact_orders aggregate
SELECT
  order_date,
  country,
  COUNT(DISTINCT order_id) AS order_cnt,
  SUM(order_amount) AS gross_order_amount
FROM silver_orders
WHERE order_date BETWEEN '${start_date}' AND '${end_date}'
GROUP BY order_date, country;


-- 4) Gold fact_payments aggregate
SELECT
  payment_date,
  country,
  COUNT(DISTINCT payment_id) AS payment_cnt,
  SUM(payment_amount) AS gross_payment_amount
FROM silver_payments
WHERE payment_date BETWEEN '${start_date}' AND '${end_date}'
GROUP BY payment_date, country;


-- 5) SCD2 dim_customer staging (hash-diff)
WITH staged AS (
  SELECT
    customer_id,
    customer_name,
    customer_tier,
    country,
    updated_at AS effective_start_ts,
    SHA2(CONCAT_WS('||',
      COALESCE(customer_name, ''),
      COALESCE(customer_tier, ''),
      COALESCE(country, '')
    ), 256) AS record_hash
  FROM silver_customers
  WHERE ingest_date = '${run_date}'
)
SELECT * FROM staged;


-- 6) Reconciliation summary
SELECT
  '${run_date}' AS run_date,
  (SELECT COUNT(*) FROM bronze_orders WHERE ingest_date = '${run_date}') AS bronze_orders_cnt,
  (SELECT COUNT(*) FROM silver_orders WHERE ingest_date = '${run_date}') AS silver_orders_cnt,
  (SELECT COUNT(*) FROM gold_fact_orders WHERE order_date = '${run_date}') AS gold_orders_cnt;
