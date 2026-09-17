import pytest
from pyspark.sql import SparkSession

from neso_emissions.formulas.emissions import activity_times_factor


@pytest.fixture(scope="module")
def spark():
    session = (
        SparkSession.builder
        .master("local[2]")
        .appName("formula-tests")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )
    yield session
    session.stop()


def test_activity_times_factor(spark):
    df = spark.createDataFrame([(100.0, 0.25)], ["activity", "factor"])
    result = activity_times_factor(df, "activity", "factor")

    assert result.first()["emissions_co2e"] == pytest.approx(25.0)
