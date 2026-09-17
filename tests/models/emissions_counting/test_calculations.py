import pytest
from pyspark.sql import SparkSession
from models.emissions_counting.modelling.calculations import calculate
def test_calculation():
    s=SparkSession.builder.master("local[2]").appName("model").config("spark.ui.enabled","false").getOrCreate()
    try:
        df=s.createDataFrame([("BASE","Road","GB",2025,100.0,0.25)],['scenario_id','sector','geography','year','activity','emission_factor'])
        assert calculate(df).first()['emissions_co2e']==pytest.approx(25.0)
    finally: s.stop()
