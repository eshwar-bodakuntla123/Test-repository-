from pyspark.sql import DataFrame
from pyspark.sql import functions as F

def validate_year_range(df: DataFrame, start_year: int, end_year: int) -> None:
    if df.filter((F.col("year") < start_year) | (F.col("year") > end_year)).limit(1).count():
        raise ValueError(f"Year outside configured range {start_year}-{end_year}")
