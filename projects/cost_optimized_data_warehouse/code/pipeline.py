from pyspark.sql import SparkSession, functions as F


def build_spark():
    return (
        SparkSession.builder
        .appName("cost_optimized_data_warehouse")
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.sql.shuffle.partitions", "400")
        .getOrCreate()
    )


def load_incremental(spark):
    return (
        spark.read.format("parquet")
        .load("s3://de-bronze/warehouse/orders/")
        .withColumn("event_date", F.to_date("order_ts"))
    )


def transform(df):
    return (
        df.dropDuplicates(["order_id"])
        .withColumn("gross_amount", F.col("quantity") * F.col("unit_price"))
        .withColumn("net_amount", F.col("gross_amount") - F.coalesce(F.col("discount_amount"), F.lit(0.0)))
    )


def write_tables(df):
    (
        df.write.mode("append")
        .format("delta")
        .partitionBy("event_date")
        .saveAsTable("silver.orders")
    )

    mart = (
        df.groupBy("event_date", "country", "channel")
        .agg(
            F.countDistinct("order_id").alias("orders"),
            F.sum("net_amount").alias("revenue")
        )
    )

    mart.write.mode("append").format("delta").saveAsTable("gold.sales_daily")


def main():
    spark = build_spark()
    bronze = load_incremental(spark)
    silver = transform(bronze)
    write_tables(silver)


if __name__ == "__main__":
    main()
