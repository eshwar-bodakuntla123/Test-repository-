"""Emissions Counting dashboard output."""

from pyspark.sql import DataFrame

from neso_model_framework.outputs.contracts import dashboard_contract


def build(df: DataFrame, model_run_id: str) -> DataFrame:
    """Create the stable dashboard output contract."""
    return dashboard_contract(
        df,
        model_run_id=model_run_id,
        formula_version="TBD-SME",
        adjustment_version="TBD",
    )
