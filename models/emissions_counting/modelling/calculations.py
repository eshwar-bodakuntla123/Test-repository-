from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from models.emissions_counting.formulas.calculations import generic_activity_factor

def calculate(df: DataFrame) -> DataFrame:
    return generic_activity_factor(df).withColumn("scope_1_2_total_co2e", F.coalesce(F.col("emissions_co2e"), F.lit(0.0)))
