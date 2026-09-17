"""Databricks model execution entry point."""

from __future__ import annotations

import argparse

from neso_model_framework.common.config import load_settings
from neso_model_framework.common.spark import create_spark
from models.emissions_counting.pipeline import run


def main() -> None:
    """Execute the requested model on Databricks compute."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="emissions_counting")
    parser.add_argument("--env", default="prod")
    args = parser.parse_args()

    if args.model != "emissions_counting":
        raise ValueError(f"Unsupported model: {args.model}")

    spark = create_spark(f"NESO-{args.model}")
    try:
        run(spark, load_settings(args.env))
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
