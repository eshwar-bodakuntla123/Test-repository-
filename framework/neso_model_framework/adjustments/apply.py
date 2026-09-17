"""Controlled application of approved SME adjustments."""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from neso_model_framework.common.exceptions import AdjustmentError


def apply_approved_adjustments(
    base_df: DataFrame,
    adjustments_df: DataFrame,
    key_columns: list[str],
    value_column: str,
    adjustment_value_column: str,
) -> DataFrame:
    """Apply approved adjustments without mutating the source dataset.

    Args:
        base_df: Canonical model input.
        adjustments_df: SME adjustment records.
        key_columns: Business key identifying the adjusted record.
        value_column: Base value to replace when an approved adjustment exists.
        adjustment_value_column: New SME-approved value.

    Returns:
        Adjusted DataFrame.

    Raises:
        AdjustmentError: If required adjustment metadata is missing.
    """
    required = set(key_columns + [adjustment_value_column, "approval_status"])
    missing = required.difference(adjustments_df.columns)
    if missing:
        raise AdjustmentError(f"Adjustment dataset is missing columns: {sorted(missing)}")

    approved = adjustments_df.filter(
        F.lower(F.col("approval_status")) == F.lit("approved")
    )

    values = approved.select(
        *key_columns,
        F.col(adjustment_value_column).cast("double").alias("_adjustment"),
    )

    return (
        base_df.join(values, key_columns, "left")
        .withColumn(
            value_column,
            F.when(F.col("_adjustment").isNotNull(), F.col("_adjustment"))
            .otherwise(F.col(value_column)),
        )
        .drop("_adjustment")
    )
