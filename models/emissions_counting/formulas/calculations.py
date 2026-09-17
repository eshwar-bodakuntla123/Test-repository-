"""Emissions Counting business formulas.

The formula below is deliberately a technical smoke-test placeholder.
It must be replaced with SME-approved reverse-engineered NESO formulas.
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def generic_activity_factor(df: DataFrame) -> DataFrame:
    """Apply the technical activity × factor smoke-test formula."""
    return df.withColumn(
        "emissions_co2e",
        F.col("activity").cast("double") * F.col("emission_factor").cast("double"),
    )
