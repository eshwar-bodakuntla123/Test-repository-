import pytest
from pyspark.sql import SparkSession

from neso_emissions.validation.checks import no_nulls, unique_key


@pytest.fixture(scope="module")
def spark():
    session = (
        SparkSession.builder
        .master("local[2]")
        .appName("dq-tests")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )
    yield session
    session.stop()


def test_no_nulls_passes(spark):
    df = spark.createDataFrame([(1,), (2,)], ["id"])
    assert no_nulls(df, ["id"]).passed


def test_no_nulls_fails(spark):
    df = spark.createDataFrame([(1,), (None,)], ["id"])
    assert not no_nulls(df, ["id"]).passed


def test_unique_key_passes(spark):
    df = spark.createDataFrame([(1,), (2,)], ["id"])
    assert unique_key(df, ["id"]).passed
