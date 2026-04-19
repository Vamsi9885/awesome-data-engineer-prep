from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window

spark = (
    SparkSession.builder
    .appName("real-time-ride-tracking-system")
    .config("spark.sql.adaptive.enabled", "true")
    .config("spark.sql.shuffle.partitions", "1200")
    .getOrCreate()
)

INPUT_STREAM = "delta.`/mnt/stream_ingress/ride_events`"  # replace with Kafka/Kinesis/EventHubs/PubSub connector
BRONZE_TABLE = "rides.bronze_events"
SILVER_TABLE = "rides.silver_events"
GOLD_ACTIVE_TABLE = "rides.gold_active_rides_1min"


def parse_and_validate(df):
    return (
        df.select(
            F.col("event_id").cast("string"),
            F.col("ride_id").cast("string"),
            F.col("driver_id").cast("string"),
            F.col("rider_id").cast("string"),
            F.col("city_id").cast("string"),
            F.col("event_type").cast("string"),
            F.to_timestamp("event_ts").alias("event_ts"),
            F.current_timestamp().alias("ingest_ts"),
            F.col("lat").cast("double"),
            F.col("lon").cast("double"),
            F.col("event_version").cast("int")
        )
        .filter(F.col("ride_id").isNotNull())
        .filter(F.col("event_ts").isNotNull())
        .filter(F.col("event_type").isin(
            "ride_requested", "driver_assigned", "trip_started",
            "location_ping", "trip_completed", "trip_canceled"
        ))
    )


def dedupe_stream(df):
    return (
        df.withWatermark("event_ts", "15 minutes")
          .dropDuplicates(["event_id"])
    )


def write_bronze(df):
    return (
        df.writeStream
          .format("delta")
          .option("checkpointLocation", "/mnt/checkpoints/rides/bronze")
          .outputMode("append")
          .toTable(BRONZE_TABLE)
    )


def build_active_rides(df):
    # active = requested/assigned/started not yet completed/canceled in the latest event snapshot
    w = Window.partitionBy("ride_id").orderBy(F.col("event_ts").desc(), F.col("ingest_ts").desc())
    latest = (
        df.withColumn("rn", F.row_number().over(w))
          .filter(F.col("rn") == 1)
          .drop("rn")
    )

    active = latest.filter(F.col("event_type").isin("ride_requested", "driver_assigned", "trip_started"))

    return (
        active.withWatermark("event_ts", "15 minutes")
              .groupBy(
                  F.window("event_ts", "1 minute", "1 minute"),
                  F.col("city_id")
              )
              .agg(F.countDistinct("ride_id").alias("active_rides"))
              .select(
                  F.col("window.start").alias("window_start"),
                  F.col("window.end").alias("window_end"),
                  F.col("city_id"),
                  F.col("active_rides")
              )
    )


def main():
    raw_stream = spark.readStream.format("delta").load("/mnt/stream_ingress/ride_events")
    parsed = parse_and_validate(raw_stream)

    bronze_query = write_bronze(parsed)

    silver_stream = dedupe_stream(parsed)
    silver_query = (
        silver_stream.writeStream
                   .format("delta")
                   .option("checkpointLocation", "/mnt/checkpoints/rides/silver")
                   .outputMode("append")
                   .toTable(SILVER_TABLE)
    )

    gold_stream = build_active_rides(silver_stream)
    gold_query = (
        gold_stream.writeStream
                  .format("delta")
                  .option("checkpointLocation", "/mnt/checkpoints/rides/gold_active")
                  .outputMode("append")
                  .toTable(GOLD_ACTIVE_TABLE)
    )

    bronze_query.awaitTermination()
    silver_query.awaitTermination()
    gold_query.awaitTermination()


if __name__ == "__main__":
    main()
