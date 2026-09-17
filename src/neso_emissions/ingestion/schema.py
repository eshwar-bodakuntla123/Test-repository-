from __future__ import annotations

from pyspark.sql import DataFrame


def assert_required_columns(df: DataFrame, columns: list[str]) -> None:
    missing = [column for column in columns if column not in df.columns]

    if missing:
        raise ValueError(f"Missing required columns: {missing}")
