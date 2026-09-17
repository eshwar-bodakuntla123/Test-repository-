"""Excel/SME golden-data reconciliation utilities."""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from neso_model_framework.common.exceptions import ReconciliationError


def compare_numeric(
    actual: DataFrame,
    expected: DataFrame,
    keys: list[str],
    actual_column: str,
    expected_column: str,
    tolerance: float,
) -> DataFrame:
    """Compare actual model values against approved expected values.

    Args:
        actual: PySpark model result.
        expected: Excel/SME golden dataset.
        keys: Business key columns.
        actual_column: Actual numeric result.
        expected_column: Expected numeric result.
        tolerance: Approved absolute tolerance.

    Returns:
        Row-level reconciliation result.
    """
    if tolerance < 0:
        raise ReconciliationError("Tolerance cannot be negative.")

    joined = actual.alias("a").join(expected.alias("e"), keys, "inner")

    return joined.select(
        *[F.col(f"a.{key}").alias(key) for key in keys],
        F.col(f"a.{actual_column}").alias("actual"),
        F.col(f"e.{expected_column}").alias("expected"),
        (
            F.abs(
                F.col(f"a.{actual_column}").cast("double")
                - F.col(f"e.{expected_column}").cast("double")
            ) <= F.lit(tolerance)
        ).alias("within_tolerance"),
    )
