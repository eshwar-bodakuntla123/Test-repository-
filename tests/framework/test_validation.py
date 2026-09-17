from neso_model_framework.validation.checks import no_nulls, required_columns, unique_key


def test_validation_checks(spark):
    df = spark.createDataFrame([(1,), (2,)], ["id"])

    assert required_columns(df, ["id"]).passed
    assert no_nulls(df, ["id"]).passed
    assert unique_key(df, ["id"]).passed
