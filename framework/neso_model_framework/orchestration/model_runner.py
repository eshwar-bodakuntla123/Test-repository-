"""Common model execution interface."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from pyspark.sql import DataFrame, SparkSession


class Model(Protocol):
    """Protocol implemented by a model pipeline."""

    def run(self, spark: SparkSession) -> DataFrame:
        """Execute the model."""
        ...


@dataclass
class ModelRunner:
    """Execute a model through a common orchestration interface."""

    model: Model

    def run(self, spark: SparkSession) -> DataFrame:
        """Run the configured model."""
        return self.model.run(spark)
