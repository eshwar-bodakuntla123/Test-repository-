"""Emissions Counting-specific validation rules."""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from neso_model_framework.common.exceptions import ValidationError


def validate_year_range(df: DataFrame, start_year: int, end_year: int) -> None:
    """Validate that model years fall within the configured range."""
    invalid = df.filter(
        (F.col("year") < start_year) | (F.col("year") > end_year)
    ).limit(1).count()

    if invalid:
        raise ValidationError(
            f"Year outside configured range {start_year}-{end_year}."
        )
