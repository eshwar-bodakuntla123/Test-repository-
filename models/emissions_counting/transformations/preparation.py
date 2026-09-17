"""Emissions Counting input preparation."""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def prepare_inputs(df: DataFrame) -> DataFrame:
    """Cast canonical model fields to calculation-safe types."""
    return (
        df.withColumn("year", F.col("year").cast("int"))
        .withColumn("activity", F.col("activity").cast("double"))
        .withColumn("emission_factor", F.col("emission_factor").cast("double"))
    )
