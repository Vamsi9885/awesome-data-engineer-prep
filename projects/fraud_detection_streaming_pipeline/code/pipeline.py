from pyspark.sql import SparkSession, functions as F


def get_spark():
    return (
        SparkSession.builder
        .appName("fraud_detection_streaming_pipeline")
        .config("spark.sql.adaptive.enabled", "true")
        .getOrCreate()
    )


def read_stream(spark):
    return (
        spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", "localhost:9092")
        .option("subscribe", "card_transactions")
        .load()
        .selectExpr("CAST(value AS STRING) as payload", "timestamp as ingestion_ts")
    )


def compute_features(df):
    base = df.withColumn("transaction_id", F.sha2(F.col("payload"), 256))
    velocity = (
        base
        .withColumn("event_ts", F.col("ingestion_ts"))
        .withWatermark("event_ts", "10 minutes")
        .groupBy(F.window("event_ts", "1 minute"))
        .agg(F.count("*").alias("txn_count_1m"))
    )
    return base, velocity


def score(base_df):
    return (
        base_df
        .withColumn("risk_score", (F.length(F.col("payload")) % F.lit(100)).cast("int"))
        .withColumn(
            "decision",
            F.when(F.col("risk_score") >= 70, F.lit("REVIEW")).otherwise(F.lit("APPROVE"))
        )
    )


def main():
    spark = get_spark()
    stream_df = read_stream(spark)
    base_df, velocity_df = compute_features(stream_df)
    scored = score(base_df)

    decision_query = (
        scored.writeStream
        .format("delta")
        .outputMode("append")
        .option("checkpointLocation", "s3://fraud/checkpoints/decisions/")
        .start("s3://fraud/gold/decisions/")
    )

    velocity_query = (
        velocity_df.writeStream
        .format("delta")
        .outputMode("update")
        .option("checkpointLocation", "s3://fraud/checkpoints/features/")
        .start("s3://fraud/silver/features/")
    )

    decision_query.awaitTermination()
    velocity_query.awaitTermination()


if __name__ == "__main__":
    main()
