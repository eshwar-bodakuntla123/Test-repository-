from __future__ import annotations

import argparse

from neso_emissions.common.config import load_settings
from neso_emissions.common.logging import get_logger
from neso_emissions.common.spark import create_spark


def run(env: str) -> None:
    settings = load_settings(env)
    logger = get_logger()

    spark = create_spark(
        app_name=f"NESO-Emissions-{env}",
        local=True,
    )

    # Local smoke-test data keeps the first repository runnable before client tables are available.
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

    from neso_emissions.modelling.emissions import calculate

    result = calculate(df)
    result.show(truncate=False)

    logger.info("Local run completed for %s", env)
    spark.stop()


def main() -> None:
    parser = argparse.ArgumentParser(prog="neso-emissions")
    sub = parser.add_subparsers(dest="command", required=True)

    run_parser = sub.add_parser("run")
    run_parser.add_argument("--env", default="dev", choices=["dev", "test", "prod"])

    args = parser.parse_args()

    if args.command == "run":
        run(args.env)


if __name__ == "__main__":
    main()
