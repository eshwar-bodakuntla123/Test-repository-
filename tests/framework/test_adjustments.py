from neso_model_framework.adjustments.apply import apply_approved_adjustments


def test_only_approved_adjustments_are_applied(spark):
    base = spark.createDataFrame(
        [("A", 100.0)],
        ["id", "value"],
    )
    adjustments = spark.createDataFrame(
        [
            ("A", 110.0, "approved"),
            ("B", 200.0, "draft"),
        ],
        ["id", "new_value", "approval_status"],
    )

    result = apply_approved_adjustments(
        base, adjustments, ["id"], "value", "new_value"
    )

    assert result.first()["value"] == 110.0
