"""Spark session construction."""

from pyspark.sql import SparkSession


def create_spark(app_name: str, local: bool = False) -> SparkSession:
    """Create or obtain a SparkSession.

    Args:
        app_name: Application name shown in Spark/Databricks.
        local: Whether to configure local[*] execution for developer testing.

    Returns:
        Active SparkSession.
    """
    builder = SparkSession.builder.appName(app_name)

    if local:
        builder = (
            builder.master("local[*]")
            .config("spark.sql.shuffle.partitions", "4")
            .config("spark.ui.enabled", "false")
        )

    return builder.getOrCreate()
