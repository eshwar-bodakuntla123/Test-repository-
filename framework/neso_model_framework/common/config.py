"""Typed environment configuration loading."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from neso_model_framework.common.exceptions import ConfigurationError


@dataclass(frozen=True)
class Settings:
    """Immutable application settings loaded from an environment YAML file."""

    environment: str
    catalog: str
    start_year: int
    end_year: int
    default_geography: str
    log_level: str


def load_settings(environment: str, base_dir: Path | None = None) -> Settings:
    """Load and validate settings for the requested environment."""
    base_dir = base_dir or Path(__file__).resolve().parents[3]
    path = base_dir / "config" / f"{environment}.yml"

    try:
        with path.open("r", encoding="utf-8") as handle:
            cfg: dict[str, Any] = yaml.safe_load(handle)
        defaults = cfg["model_defaults"]
        return Settings(
            environment=str(cfg["environment"]),
            catalog=str(cfg["catalog"]),
            start_year=int(defaults["start_year"]),
            end_year=int(defaults["end_year"]),
            default_geography=str(defaults["default_geography"]),
            log_level=str(defaults["log_level"]),
        )
    except (OSError, KeyError, TypeError, ValueError, yaml.YAMLError) as exc:
        raise ConfigurationError(f"Invalid configuration: {path}") from exc
