from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def compare_numeric_column(
    actual: DataFrame,
    expected: DataFrame,
    keys: list[str],
    actual_column: str,
    expected_column: str,
    tolerance: float = 1e-9,
) -> DataFrame:
    """
    Compare PySpark output to an Excel/SME golden dataset.

    Expected data should be exported from the approved Excel reference and treated as test data.
    """
    joined = actual.alias("a").join(expected.alias("e"), keys, "inner")

    return joined.select(
        *[F.col(f"a.{key}").alias(key) for key in keys],
        F.col(f"a.{actual_column}").alias("actual"),
        F.col(f"e.{expected_column}").alias("expected"),
        (
            F.abs(
                F.col(f"a.{actual_column}").cast("double")
                - F.col(f"e.{expected_column}").cast("double")
            )
            <= F.lit(tolerance)
        ).alias("within_tolerance"),
    )
