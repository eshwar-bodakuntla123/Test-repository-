from pyspark.sql import SparkSession

def create_spark(app_name: str, local: bool = False) -> SparkSession:
    builder = SparkSession.builder.appName(app_name)
    if local:
        builder = builder.master("local[*]").config("spark.sql.shuffle.partitions", "4").config("spark.ui.enabled", "false")
    return builder.getOrCreate()
