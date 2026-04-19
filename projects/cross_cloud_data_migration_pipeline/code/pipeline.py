from pyspark.sql import SparkSession, functions as F, Window


def build_spark():
    return (
        SparkSession.builder
        .appName("cross_cloud_data_migration_pipeline")
        .config("spark.sql.adaptive.enabled", "true")
        .getOrCreate()
    )


def load_source(spark):
    return spark.read.format("parquet").load("s3://source-lake/raw/")


def dedup_cdc(df):
    w = Window.partitionBy("table_name", "pk", "op_ts").orderBy(F.col("ingestion_ts").desc())
    return df.withColumn("rn", F.row_number().over(w)).filter("rn = 1").drop("rn")


def validate(df):
    return (
        df.withColumn("row_checksum", F.sha2(F.concat_ws("||", *[F.coalesce(F.col(c).cast("string"), F.lit("")) for c in df.columns]), 256))
    )


def write_target(df):
    (
        df.write.mode("append")
        .format("delta")
        .partitionBy("table_name")
        .save("gs://target-lake/bronze/migrated/")
    )


def main():
    spark = build_spark()
    source = load_source(spark).withColumn("ingestion_ts", F.current_timestamp())
    deduped = dedup_cdc(source)
    validated = validate(deduped)
    write_target(validated)


if __name__ == "__main__":
    main()
