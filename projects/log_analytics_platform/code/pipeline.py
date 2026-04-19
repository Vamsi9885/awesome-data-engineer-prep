from pyspark.sql import SparkSession, functions as F, Window


def build_spark():
    return (
        SparkSession.builder
        .appName("log_analytics_platform")
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.sql.shuffle.partitions", "600")
        .getOrCreate()
    )


def parse_logs(df):
    return (
        df.withColumn("event_ts", F.to_timestamp("timestamp"))
        .withColumn("event_date", F.to_date("event_ts"))
        .withColumn("severity", F.upper(F.col("severity")))
        .withColumn("message_hash", F.sha2(F.coalesce(F.col("message"), F.lit("")), 256))
    )


def apply_quality(df):
    valid = (
        df.filter(F.col("event_ts").isNotNull())
        .filter(F.col("service_name").isNotNull())
        .filter(F.col("severity").isin("DEBUG", "INFO", "WARN", "ERROR", "FATAL"))
    )
    invalid = df.subtract(valid)
    return valid, invalid


def dedup(df):
    w = Window.partitionBy("event_id").orderBy(F.col("ingestion_ts").desc())
    return (
        df.withColumn("rn", F.row_number().over(w))
        .filter(F.col("rn") == 1)
        .drop("rn")
    )


def main():
    spark = build_spark()

    raw = spark.read.format("json").load("s3://de-bronze/logs/")
    parsed = parse_logs(raw).withColumn("ingestion_ts", F.current_timestamp())
    valid, invalid = apply_quality(parsed)
    curated = dedup(valid)

    curated.write.mode("append").format("delta").partitionBy("event_date", "service_name").saveAsTable("silver.logs_curated")
    invalid.write.mode("append").format("parquet").save("s3://de-dlq/logs/")

    curated.createOrReplaceTempView("logs_curated")
    agg = spark.sql(
        """
        SELECT
          event_date,
          service_name,
          severity,
          COUNT(*) AS log_count
        FROM logs_curated
        GROUP BY event_date, service_name, severity
        """
    )

    agg.write.mode("append").format("delta").saveAsTable("gold.logs_aggregates")


if __name__ == "__main__":
    main()
