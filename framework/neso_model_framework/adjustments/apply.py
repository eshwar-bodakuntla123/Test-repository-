from pyspark.sql import DataFrame
from pyspark.sql import functions as F
def apply_approved_adjustments(base_df: DataFrame, adjustments_df: DataFrame, key_columns: list[str], value_column: str, adjustment_value_column: str) -> DataFrame:
    a=adjustments_df.filter(F.lower(F.col("approval_status"))=="approved").select(*key_columns,F.col(adjustment_value_column).cast("double").alias("_adjustment"))
    return base_df.join(a,key_columns,"left").withColumn(value_column,F.when(F.col("_adjustment").isNotNull(),F.col("_adjustment")).otherwise(F.col(value_column))).drop("_adjustment")
