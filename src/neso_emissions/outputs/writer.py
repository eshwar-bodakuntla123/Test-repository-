from __future__ import annotations

from pyspark.sql import DataFrame


def write_table(df: DataFrame, table_name: str, mode: str = "overwrite") -> None:
    df.write.format("delta").mode(mode).saveAsTable(table_name)
