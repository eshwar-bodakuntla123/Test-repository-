"""Stable model output contracts."""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def dashboard_contract(
    df: DataFrame,
    model_run_id: str,
    formula_version: str,
    adjustment_version: str,
) -> DataFrame:
    """Build the common dashboard-facing output contract."""
    return df.select(
        F.lit(model_run_id).alias("model_run_id"),
        "scenario_id",
        "sector",
        "geography",
        "year",
        F.lit("scope_1_2_emissions").alias("metric"),
        F.lit("tCO2e").alias("unit"),
        F.col("emissions_co2e").cast("double").alias("value"),
        F.lit(formula_version).alias("formula_version"),
        F.lit(adjustment_version).alias("adjustment_version"),
        F.lit("DRAFT").alias("approval_status"),
    )
