from neso_model_framework.common.config import Settings
from neso_model_framework.common.run_context import RunContext
from neso_model_framework.validation.checks import assert_passed, no_nulls, required_columns
from models.emissions_counting.transformations.preparation import prepare_inputs
from models.emissions_counting.validation.business_rules import validate_year_range
from models.emissions_counting.modelling.calculations import calculate
from models.emissions_counting.outputs.dashboard import build

def run(spark, settings: Settings):
    context = RunContext.create(settings.environment)
    df = spark.createDataFrame([("BASE", "Road", "GB", 2025, 100.0, 0.25), ("BASE", "Power", "GB", 2030, 200.0, 0.10)], ["scenario_id", "sector", "geography", "year", "activity", "emission_factor"])
    assert_passed([required_columns(df, list(settings.__dict__.keys()) if False else ["scenario_id","sector","geography","year","activity","emission_factor"]), no_nulls(df, ["scenario_id","sector","geography","year","activity","emission_factor"])])
    prepared = prepare_inputs(df)
    validate_year_range(prepared, settings.start_year, settings.end_year)
    return build(calculate(prepared), context.model_run_id)
