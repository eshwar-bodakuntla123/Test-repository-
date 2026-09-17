from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .registry import FORMULAS


@FORMULAS.register("GENERIC_ACTIVITY_FACTOR")
def activity_times_factor(
    df: DataFrame,
    activity_col: str,
    factor_col: str,
    output_col: str = "emissions_co2e",
) -> DataFrame:
    """
    Generic framework example only.

    DO NOT treat this as an NESO-approved formula.
    Replace/extend this with the SME reverse-engineered formula and explicit unit conversion.
    """
    return df.withColumn(
        output_col,
        F.col(activity_col).cast("double")
        * F.col(factor_col).cast("double"),
    )
