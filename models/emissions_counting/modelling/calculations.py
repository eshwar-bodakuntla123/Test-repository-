"""Emissions Counting calculation orchestration."""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from models.emissions_counting.formulas.calculations import generic_activity_factor


def calculate(df: DataFrame) -> DataFrame:
    """Calculate the current model result using registered model rules."""
    result = generic_activity_factor(df)
    return result.withColumn(
        "scope_1_2_total_co2e",
        F.coalesce(F.col("emissions_co2e"), F.lit(0.0)),
    )
