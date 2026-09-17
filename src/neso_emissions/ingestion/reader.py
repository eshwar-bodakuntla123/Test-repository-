from __future__ import annotations

from pyspark.sql import DataFrame, SparkSession


def read_table(spark: SparkSession, table_name: str) -> DataFrame:
    return spark.table(table_name)


def read_delta(spark: SparkSession, path: str) -> DataFrame:
    return spark.read.format("delta").load(path)


def read_csv(spark: SparkSession, path: str) -> DataFrame:
    return (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv(path)
    )
