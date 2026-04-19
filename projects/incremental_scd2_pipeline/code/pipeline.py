from pyspark.sql import SparkSession, functions as F, Window


def build_spark():
    return (
        SparkSession.builder
        .appName("incremental_scd2_pipeline")
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.sql.shuffle.partitions", "400")
        .getOrCreate()
    )


def normalize_and_hash(df):
    tracked_cols = ["customer_name", "tier", "city", "risk_score", "segment"]
    df2 = (
        df.withColumn("event_ts", F.to_timestamp("event_ts"))
        .withColumn("ingestion_ts", F.current_timestamp())
        .withColumn(
            "record_hash",
            F.sha2(
                F.concat_ws(
                    "||",
                    *[F.coalesce(F.col(c).cast("string"), F.lit("")) for c in tracked_cols]
                ),
                256,
            ),
        )
    )
    return df2


def deduplicate(df):
    w = Window.partitionBy("customer_id", "event_ts", "source_seq_id").orderBy(
        F.col("ingestion_ts").desc()
    )
    return df.withColumn("rn", F.row_number().over(w)).filter(F.col("rn") == 1).drop("rn")


def mark_effective_dates(df):
    return (
        df.withColumn("effective_start_ts", F.col("event_ts"))
        .withColumn("effective_end_ts", F.to_timestamp(F.lit("9999-12-31 00:00:00")))
        .withColumn("is_current", F.lit(True))
    )


def main():
    spark = build_spark()

    # Placeholder source - replace with real streaming source config
    source_df = spark.read.format("parquet").load("s3://de-bronze/customer_cdc/")
    prepared = mark_effective_dates(deduplicate(normalize_and_hash(source_df)))

    prepared.createOrReplaceTempView("staged_changes")

    # In production use Delta/Iceberg MERGE with transactional sink
    merge_sql = """
    MERGE INTO gold.dim_customer_scd2 t
    USING staged_changes s
    ON t.customer_id = s.customer_id AND t.is_current = true
    WHEN MATCHED AND t.record_hash <> s.record_hash THEN
      UPDATE SET
        t.effective_end_ts = s.effective_start_ts - INTERVAL 1 MICROSECOND,
        t.is_current = false,
        t.updated_at = current_timestamp()
    WHEN NOT MATCHED THEN
      INSERT (
        customer_id, customer_name, tier, city, risk_score, segment,
        record_hash, effective_start_ts, effective_end_ts, is_current,
        source_system, source_seq_id, ingestion_ts
      )
      VALUES (
        s.customer_id, s.customer_name, s.tier, s.city, s.risk_score, s.segment,
        s.record_hash, s.effective_start_ts, s.effective_end_ts, s.is_current,
        s.source_system, s.source_seq_id, s.ingestion_ts
      )
    """

    spark.sql(merge_sql)

    count_processed = prepared.count()
    audit = (
        spark.createDataFrame(
            [("incremental_scd2_pipeline", count_processed)],
            ["pipeline_name", "records_processed"],
        )
        .withColumn("processed_at", F.current_timestamp())
    )

    audit.write.mode("append").format("delta").saveAsTable("ops.scd2_batch_audit")


if __name__ == "__main__":
    main()
