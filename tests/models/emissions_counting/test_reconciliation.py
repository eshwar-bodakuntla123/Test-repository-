from pyspark.sql import SparkSession
from neso_model_framework.reconciliation.comparator import compare_numeric
def test_reconciliation():
    s=SparkSession.builder.master("local[2]").appName("rec").config("spark.ui.enabled","false").getOrCreate()
    try:
        a=s.createDataFrame([('A',25.0000001)],['id','value']); e=s.createDataFrame([('A',25.0)],['id','expected'])
        assert compare_numeric(a,e,['id'],'value','expected',1e-5).first()['within_tolerance']
    finally: s.stop()
