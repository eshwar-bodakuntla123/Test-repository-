"""Command-line entry point."""

from __future__ import annotations

import argparse

from neso_model_framework.common.config import load_settings
from neso_model_framework.common.logging import get_logger
from neso_model_framework.common.spark import create_spark


def main() -> None:
    """Parse CLI arguments and execute a model."""
    parser = argparse.ArgumentParser(prog="neso-model")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run")
    run.add_argument("model")
    run.add_argument("--env", default="dev", choices=["dev", "test", "prod"])
    run.add_argument("--local", action="store_true")

    args = parser.parse_args()

    if args.command != "run":
        raise ValueError(f"Unsupported command: {args.command}")

    if args.model != "emissions_counting":
        raise ValueError(
            "Starter implementation contains emissions_counting. "
            "Add the requested model under models/."
        )

    settings = load_settings(args.env)
    spark = create_spark(f"NESO-{args.model}-{args.env}", local=args.local)

    try:
        from models.emissions_counting.pipeline import run
        run(spark, settings)
        get_logger(model=args.model, pipeline=args.model, task="run").info(
            "Model execution completed"
        )
    finally:
        spark.stop()
