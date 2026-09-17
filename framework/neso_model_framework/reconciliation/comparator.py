from pyspark.sql import DataFrame
from pyspark.sql import functions as F
def compare_numeric(actual: DataFrame, expected: DataFrame, keys: list[str], actual_column: str, expected_column: str, tolerance: float) -> DataFrame:
    j=actual.alias("a").join(expected.alias("e"), keys, "inner")
    return j.select(*[F.col(f"a.{k}").alias(k) for k in keys], F.col(f"a.{actual_column}").alias("actual"), F.col(f"e.{expected_column}").alias("expected"), (F.abs(F.col(f"a.{actual_column}").cast("double")-F.col(f"e.{expected_column}").cast("double"))<=F.lit(tolerance)).alias("within_tolerance"))
