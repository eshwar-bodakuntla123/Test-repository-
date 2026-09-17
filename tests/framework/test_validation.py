from pyspark.sql import SparkSession
from neso_model_framework.validation.checks import required_columns, no_nulls
def test_validation():
    s=SparkSession.builder.master("local[2]").appName("dq").config("spark.ui.enabled","false").getOrCreate()
    try:
        df=s.createDataFrame([(1,)],['id']); assert required_columns(df,['id']).passed; assert no_nulls(df,['id']).passed
    finally: s.stop()
