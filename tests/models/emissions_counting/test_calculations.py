import pytest

from models.emissions_counting.modelling.calculations import calculate


def test_emissions_calculation(spark):
    df = spark.createDataFrame(
        [("BASE", "Road", "GB", 2025, 100.0, 0.25)],
        ["scenario_id", "sector", "geography", "year", "activity", "emission_factor"],
    )

    result = calculate(df).first()
    assert result["emissions_co2e"] == pytest.approx(25.0)
