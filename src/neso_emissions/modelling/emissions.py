from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from neso_emissions.formulas.emissions import activity_times_factor


def calculate(df: DataFrame) -> DataFrame:
    """
    Compose approved SME rules here.

    The current generic rule is only a technical smoke-test placeholder.
    Real NESO formulas must be added from the reverse-engineering work.
    """
    result = activity_times_factor(
        df,
        activity_col="activity",
        factor_col="emission_factor",
        output_col="emissions_co2e",
    )

    return result.withColumn(
        "scope_12_total_co2e",
        F.coalesce(F.col("emissions_co2e"), F.lit(0.0)),
    )


def build_dashboard_output(df: DataFrame) -> DataFrame:
    """
    Stable dashboard data contract.

    The UI/API consumes this contract rather than depending on internal calculation columns.
    """
    return (
        df.select(
            "scenario_id",
            "sector",
            "geography",
            "year",
            F.col("scope_12_total_co2e").alias("emissions_co2e"),
        )
    )
