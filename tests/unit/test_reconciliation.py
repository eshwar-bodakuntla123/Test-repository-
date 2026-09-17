from pyspark.sql import SparkSession

from neso_emissions.reconciliation.excel_compare import compare_numeric_column


def test_reconciliation_within_tolerance():
    spark = (
        SparkSession.builder
        .master("local[2]")
        .appName("reconciliation-tests")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )

    try:
        actual = spark.createDataFrame([("A", 25.000000001)], ["id", "value"])
        expected = spark.createDataFrame([("A", 25.0)], ["id", "expected"])

        result = compare_numeric_column(
            actual,
            expected,
            ["id"],
            "value",
            "expected",
            tolerance=1e-6,
        )

        assert result.first()["within_tolerance"]
    finally:
        spark.stop()
