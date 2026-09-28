from pathlib import Path
import yaml


DEFAULT_CONFIG = {
    "header_rows": {"default": 1},
    "output": {
        "formulas_file": "formulas.csv",
        "dependencies_file": "dependencies.csv",
        "issues_file": "issues.csv",
    },
    "options": {
        "sanitize_names": True,
        "keep_unresolved": True,
    },
}


def load_config(path: str | None) -> dict:
    config = DEFAULT_CONFIG.copy()
    if not path:
        return config

    with Path(path).open("r", encoding="utf-8") as f:
        user = yaml.safe_load(f) or {}

    for key in ("header_rows", "output", "options"):
        if key in user and isinstance(user[key], dict):
            config[key] = {**config[key], **user[key]}

    return config


def header_row_for(config: dict, sheet_name: str) -> int:
    rows = config["header_rows"]
    return int(rows.get(sheet_name, rows.get("default", 1)))
