"""Reusable Spark input readers."""

from pyspark.sql import DataFrame, SparkSession

from neso_model_framework.common.exceptions import DataAccessError


def read_table(spark: SparkSession, table_name: str) -> DataFrame:
    """Read a managed Spark/Delta table.

    Args:
        spark: Active SparkSession.
        table_name: Fully qualified table name.

    Returns:
        Spark DataFrame.

    Raises:
        DataAccessError: If the table cannot be read.
    """
    try:
        return spark.table(table_name)
    except Exception as exc:
        raise DataAccessError(f"Unable to read table: {table_name}") from exc


def read_delta(spark: SparkSession, path: str) -> DataFrame:
    """Read a Delta path into a Spark DataFrame."""
    try:
        return spark.read.format("delta").load(path)
    except Exception as exc:
        raise DataAccessError(f"Unable to read Delta path: {path}") from exc


def read_csv(spark: SparkSession, path: str) -> DataFrame:
    """Read a headered CSV file with schema inference for local development."""
    try:
        return (
            spark.read.option("header", True)
            .option("inferSchema", True)
            .csv(path)
        )
    except Exception as exc:
        raise DataAccessError(f"Unable to read CSV path: {path}") from exc
