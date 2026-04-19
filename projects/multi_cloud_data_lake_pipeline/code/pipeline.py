from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window

spark = (
    SparkSession.builder
    .appName("multi-cloud-data-lake-pipeline")
    .config("spark.sql.adaptive.enabled", "true")
    .config("spark.sql.shuffle.partitions", "800")
    .getOrCreate()
)

RUN_ID = "manual_run_2026_01_01_00"
RUN_DATE = "2026-01-01"

BRONZE_ORDERS = "lakehouse.bronze_orders"
SILVER_ORDERS = "lakehouse.silver_orders"
GOLD_DAILY_REVENUE = "lakehouse.gold_daily_revenue_country"


def add_ingest_metadata(df, source_cloud: str, source_path: str):
    return (
        df.withColumn("source_cloud", F.lit(source_cloud))
          .withColumn("source_path", F.lit(source_path))
          .withColumn("ingest_ts", F.current_timestamp())
          .withColumn("run_id", F.lit(RUN_ID))
    )


def standardize_orders(df):
    return (
        df.withColumn("order_ts_utc", F.to_timestamp("order_ts"))
          .withColumn("event_date", F.to_date("order_ts_utc"))
          .withColumn("country_code", F.upper(F.col("country_code")))
          .withColumn(
              "order_amount_usd",
              F.when(F.col("currency_code") == F.lit("USD"), F.col("order_amount"))
               .when(F.col("currency_code") == F.lit("EUR"), F.col("order_amount") * F.lit(1.08))
               .when(F.col("currency_code") == F.lit("GBP"), F.col("order_amount") * F.lit(1.26))
               .otherwise(F.col("order_amount"))
          )
          .withColumn(
              "record_hash",
              F.sha2(
                  F.concat_ws(
                      "||",
                      F.coalesce(F.col("order_id").cast("string"), F.lit("")),
                      F.coalesce(F.col("customer_id").cast("string"), F.lit("")),
                      F.coalesce(F.col("order_ts").cast("string"), F.lit("")),
                      F.coalesce(F.col("order_amount").cast("string"), F.lit("")),
                      F.coalesce(F.col("currency_code").cast("string"), F.lit(""))
                  ),
                  256
              )
          )
    )


def dedupe_latest(df):
    w = Window.partitionBy("order_id").orderBy(F.col("order_ts_utc").desc(), F.col("ingest_ts").desc())
    return (
        df.withColumn("rn", F.row_number().over(w))
          .filter(F.col("rn") == 1)
          .drop("rn")
    )


def bronze_to_silver():
    bronze = spark.table(BRONZE_ORDERS)
    standardized = standardize_orders(bronze)
    deduped = dedupe_latest(standardized)

    (
        deduped.write
        .format("delta")
        .mode("overwrite")
        .option("replaceWhere", f"event_date = '{RUN_DATE}'")
        .saveAsTable(SILVER_ORDERS)
    )


def build_gold():
    silver = spark.table(SILVER_ORDERS).filter(F.col("event_date") == F.lit(RUN_DATE))
    daily = (
        silver.groupBy("event_date", "country_code")
              .agg(
                  F.countDistinct("order_id").alias("orders_cnt"),
                  F.sum("order_amount_usd").alias("gross_revenue_usd"),
                  F.approx_count_distinct("customer_id").alias("buyers_cnt")
              )
              .withColumnRenamed("event_date", "ds")
    )

    (
        daily.write
        .format("delta")
        .mode("overwrite")
        .option("replaceWhere", f"ds = '{RUN_DATE}'")
        .saveAsTable(GOLD_DAILY_REVENUE)
    )


def run():
    # Example multi-cloud raw reads (paths are placeholders for environment-specific mounts)
    aws_raw = spark.read.format("parquet").load("s3://global-raw/orders/ds=2026-01-01/")
    azure_raw = spark.read.format("parquet").load("abfss://raw@companyadls.dfs.core.windows.net/orders/ds=2026-01-01/")
    gcp_raw = spark.read.format("parquet").load("gs://global-raw/orders/ds=2026-01-01/")

    aws_bronze = add_ingest_metadata(aws_raw, "aws", "s3://global-raw/orders/ds=2026-01-01/")
    azure_bronze = add_ingest_metadata(azure_raw, "azure", "abfss://raw@companyadls.dfs.core.windows.net/orders/ds=2026-01-01/")
    gcp_bronze = add_ingest_metadata(gcp_raw, "gcp", "gs://global-raw/orders/ds=2026-01-01/")

    bronze_union = aws_bronze.unionByName(azure_bronze, allowMissingColumns=True).unionByName(gcp_bronze, allowMissingColumns=True)

    (
        bronze_union.write
        .format("delta")
        .mode("append")
        .partitionBy("event_date", "source_cloud")
        .saveAsTable(BRONZE_ORDERS)
    )

    bronze_to_silver()
    build_gold()


if __name__ == "__main__":
    run()
