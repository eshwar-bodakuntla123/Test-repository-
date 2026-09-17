from neso_model_framework.reconciliation.comparator import compare_numeric


def test_reconciliation_within_tolerance(spark):
    actual = spark.createDataFrame([("A", 25.0000001)], ["id", "value"])
    expected = spark.createDataFrame([("A", 25.0)], ["id", "expected"])

    result = compare_numeric(
        actual,
        expected,
        ["id"],
        "value",
        "expected",
        tolerance=1e-5,
    ).first()

    assert result["within_tolerance"]
