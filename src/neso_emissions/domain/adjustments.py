from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def apply_value_adjustments(
    base_df: DataFrame,
    adjustments_df: DataFrame,
    key_columns: list[str],
    value_column: str,
    adjustment_value_column: str,
) -> DataFrame:
    """
    Apply approved SME adjustments without mutating the source dataframe.
    """
    adjustments = adjustments_df.select(
        *key_columns,
        F.col(adjustment_value_column).cast("double").alias("_adjustment"),
    )

    return (
        base_df.join(adjustments, key_columns, "left")
        .withColumn(
            value_column,
            F.when(F.col("_adjustment").isNotNull(), F.col("_adjustment"))
            .otherwise(F.col(value_column)),
        )
        .drop("_adjustment")
    )
