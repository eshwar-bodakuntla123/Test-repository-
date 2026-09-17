from __future__ import annotations

from pyspark.sql import SparkSession

from neso_emissions.common.config import Settings
from neso_emissions.common.logging import get_logger
from neso_emissions.ingestion.reader import read_table
from neso_emissions.ingestion.schema import assert_required_columns
from neso_emissions.modelling.emissions import calculate


def run(spark: SparkSession, settings: Settings):
    logger = get_logger()
    logger.info("Reading input table %s", settings.input_table)

    df = read_table(spark, settings.input_table)
    assert_required_columns(df, list(settings.required_columns))

    result = calculate(df)

    logger.info("Emissions calculation completed")
    return result
