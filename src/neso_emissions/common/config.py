from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class Settings:
    environment: str
    model_name: str
    start_year: int
    end_year: int
    default_geography: str
    input_table: str
    output_table: str
    adjustment_table: str
    fail_on_dq_error: bool
    required_columns: tuple[str, ...]


def load_settings(env: str, base_dir: Path | None = None) -> Settings:
    base_dir = base_dir or Path(__file__).resolve().parents[3]
    path = base_dir / "config" / f"{env}.yml"

    if not path.exists():
        raise FileNotFoundError(f"Configuration not found: {path}")

    with path.open("r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)

    return Settings(
        environment=cfg["environment"],
        model_name=cfg["model"]["name"],
        start_year=cfg["model"]["start_year"],
        end_year=cfg["model"]["end_year"],
        default_geography=cfg["model"]["default_geography"],
        input_table=cfg["data"]["input_table"],
        output_table=cfg["data"]["output_table"],
        adjustment_table=cfg["data"]["adjustment_table"],
        fail_on_dq_error=cfg["dq"]["fail_on_error"],
        required_columns=tuple(cfg["dq"]["required_columns"]),
    )
