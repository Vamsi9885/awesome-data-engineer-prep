from pyspark.sql import SparkSession, functions as F, Window


def spark_session():
    return (
        SparkSession.builder
        .appName("azure_batch_adf_adls_databricks_synapse")
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.databricks.delta.optimizeWrite.enabled", "true")
        .config("spark.databricks.delta.autoCompact.enabled", "true")
        .getOrCreate()
    )


def read_raw(spark, run_date: str):
    base = "abfss://raw@adlsprod01.dfs.core.windows.net/ecomm"
    orders = spark.read.format("json").load(f"{base}/orders/dt={run_date}/*")
    payments = spark.read.format("json").load(f"{base}/payments/dt={run_date}/*")
    customers = spark.read.format("json").load(f"{base}/customers/dt={run_date}/*")
    refunds = spark.read.format("json").load(f"{base}/refunds/dt={run_date}/*")
    inventory = spark.read.option("header", "true").csv(f"{base}/inventory/dt={run_date}/*")
    return orders, payments, customers, refunds, inventory


def dedup_latest(df, key_cols, ts_col):
    w = Window.partitionBy(*key_cols).orderBy(F.col(ts_col).desc())
    return (
        df.withColumn("_rn", F.row_number().over(w))
        .filter(F.col("_rn") == 1)
        .drop("_rn")
    )


def write_bronze(orders, payments, customers, refunds, inventory, run_date: str):
    bronze = "abfss://bronze@adlsprod01.dfs.core.windows.net/ecomm"

    dedup_latest(orders, ["order_id"], "updated_at") \
        .withColumn("ingest_date", F.lit(run_date)) \
        .write.mode("append").format("delta").partitionBy("ingest_date") \
        .save(f"{bronze}/orders")

    dedup_latest(payments, ["payment_id"], "updated_at") \
        .withColumn("ingest_date", F.lit(run_date)) \
        .write.mode("append").format("delta").partitionBy("ingest_date") \
        .save(f"{bronze}/payments")

    dedup_latest(customers, ["customer_id"], "updated_at") \
        .withColumn("ingest_date", F.lit(run_date)) \
        .write.mode("append").format("delta").partitionBy("ingest_date") \
        .save(f"{bronze}/customers")

    dedup_latest(refunds, ["refund_id"], "updated_at") \
        .withColumn("ingest_date", F.lit(run_date)) \
        .write.mode("append").format("delta").partitionBy("ingest_date") \
        .save(f"{bronze}/refunds")

    inventory.withColumn("ingest_date", F.lit(run_date)) \
        .write.mode("append").format("delta").partitionBy("ingest_date") \
        .save(f"{bronze}/inventory")


def build_gold(spark, run_date: str):
    bronze = "abfss://bronze@adlsprod01.dfs.core.windows.net/ecomm"
    gold = "abfss://gold@adlsprod01.dfs.core.windows.net/ecomm"

    orders = spark.read.format("delta").load(f"{bronze}/orders").filter(F.col("ingest_date") == run_date)
    payments = spark.read.format("delta").load(f"{bronze}/payments").filter(F.col("ingest_date") == run_date)
    customers = spark.read.format("delta").load(f"{bronze}/customers").filter(F.col("ingest_date") == run_date)

    fact_orders = (
        orders.groupBy("order_date", "country")
        .agg(
            F.countDistinct("order_id").alias("order_cnt"),
            F.sum("order_amount").alias("gross_order_amount")
        )
    )

    fact_payments = (
        payments.groupBy("payment_date", "country")
        .agg(
            F.countDistinct("payment_id").alias("payment_cnt"),
            F.sum("payment_amount").alias("gross_payment_amount")
        )
    )

    dim_customer = (
        customers.select(
            "customer_id", "customer_name", "customer_tier",
            "country", "updated_at"
        )
        .withColumn("effective_start_ts", F.col("updated_at"))
        .withColumn("effective_end_ts", F.lit("9999-12-31").cast("timestamp"))
        .withColumn("is_current", F.lit(True))
    )

    fact_orders.write.mode("overwrite").format("delta").partitionBy("order_date").save(f"{gold}/fact_orders")
    fact_payments.write.mode("overwrite").format("delta").partitionBy("payment_date").save(f"{gold}/fact_payments")
    dim_customer.write.mode("overwrite").format("delta").partitionBy("country").save(f"{gold}/dim_customer")


def main(run_date: str):
    spark = spark_session()
    orders, payments, customers, refunds, inventory = read_raw(spark, run_date)
    write_bronze(orders, payments, customers, refunds, inventory, run_date)
    build_gold(spark, run_date)


if __name__ == "__main__":
    # Example: python pipeline.py 2026-01-31
    import sys
    if len(sys.argv) != 2:
        raise ValueError("Usage: python pipeline.py <run_date: YYYY-MM-DD>")
    main(sys.argv[1])
