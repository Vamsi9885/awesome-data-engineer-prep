from pyspark.sql import SparkSession, functions as F


def spark_session():
    return (
        SparkSession.builder
        .appName("lambda_hybrid_stream_batch_pipeline")
        .config("spark.sql.adaptive.enabled", "true")
        .getOrCreate()
    )


def speed_layer(spark):
    events = (
        spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", "localhost:9092")
        .option("subscribe", "marketplace_events")
        .load()
    )

    parsed = events.selectExpr("CAST(value AS STRING) as payload", "timestamp as ingestion_ts")
    metrics = (
        parsed
        .withColumn("event_ts", F.col("ingestion_ts"))
        .withWatermark("event_ts", "15 minutes")
        .groupBy(F.window("event_ts", "1 minute"))
        .agg(F.count("*").alias("events_per_minute"))
    )
    return metrics


def batch_layer(spark):
    raw = spark.read.format("parquet").load("s3://de-lambda/raw/events/")
    return (
        raw.withColumn("event_date", F.to_date("event_ts"))
        .groupBy("event_date")
        .agg(F.count("*").alias("daily_events"))
    )


def main():
    spark = spark_session()

    speed_df = speed_layer(spark)
    speed_query = (
        speed_df.writeStream
        .format("delta")
        .outputMode("update")
        .option("checkpointLocation", "s3://de-lambda/checkpoints/speed/")
        .start("s3://de-lambda/speed/")
    )

    batch_df = batch_layer(spark)
    batch_df.write.mode("overwrite").format("delta").save("s3://de-lambda/batch/")

    speed_query.awaitTermination()


if __name__ == "__main__":
    main()
