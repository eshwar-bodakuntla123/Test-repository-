"""Emissions Counting model pipeline."""

from pyspark.sql import SparkSession

from neso_model_framework.common.config import Settings
from neso_model_framework.common.logging import get_logger
from neso_model_framework.common.run_context import RunContext
from neso_model_framework.validation.checks import assert_passed, no_nulls, required_columns

from models.emissions_counting.modelling.calculations import calculate
from models.emissions_counting.outputs.dashboard import build
from models.emissions_counting.transformations.preparation import prepare_inputs
from models.emissions_counting.validation.business_rules import validate_year_range


def run(spark: SparkSession, settings: Settings):
    """Execute the Emissions Counting pipeline.

    The sample DataFrame is local smoke-test data. In production, replace it with
    the approved NESO Databricks input interface.
    """
    context = RunContext.create(settings.environment)
    logger = get_logger(
        run_id=context.model_run_id,
        model="emissions_counting",
        pipeline="emissions_counting",
        task="pipeline",
    )

    logger.info("Starting model pipeline")

    df = spark.createDataFrame(
        [
            ("BASE", "Road", "GB", 2025, 100.0, 0.25),
            ("BASE", "Power", "GB", 2030, 200.0, 0.10),
        ],
        [
            "scenario_id",
            "sector",
            "geography",
            "year",
            "activity",
            "emission_factor",
        ],
    )

    checks = [
        required_columns(
            df,
            [
                "scenario_id",
                "sector",
                "geography",
                "year",
                "activity",
                "emission_factor",
            ],
        ),
        no_nulls(
            df,
            [
                "scenario_id",
                "sector",
                "geography",
                "year",
                "activity",
                "emission_factor",
            ],
        ),
    ]
    assert_passed(checks)

    prepared = prepare_inputs(df)
    validate_year_range(prepared, settings.start_year, settings.end_year)

    calculated = calculate(prepared)
    output = build(calculated, context.model_run_id)

    logger.info("Pipeline calculation completed")
    output.show(truncate=False)
    return output
