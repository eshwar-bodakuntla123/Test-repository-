from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def generic_activity_factor(df: DataFrame) -> DataFrame:
    """Technical smoke-test only; replace with SME-approved NESO formula."""
    return df.withColumn("emissions_co2e", F.col("activity").cast("double") * F.col("emission_factor").cast("double"))
