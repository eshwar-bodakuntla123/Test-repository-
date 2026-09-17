from dataclasses import dataclass
from pathlib import Path
import yaml
@dataclass(frozen=True)
class Settings:
    environment: str
    catalog: str
    start_year: int
    end_year: int
    default_geography: str
def load_settings(environment: str, base_dir: Path | None = None) -> Settings:
    base_dir = base_dir or Path(__file__).resolve().parents[3]
    with (base_dir / "config" / f"{environment}.yml").open(encoding="utf-8") as f: cfg = yaml.safe_load(f)
    d = cfg["model_defaults"]
    return Settings(cfg["environment"], cfg["catalog"], d["start_year"], d["end_year"], d["default_geography"])
