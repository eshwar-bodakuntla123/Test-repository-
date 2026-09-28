import csv
from pathlib import Path


def write_csv(path: Path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()

        for row in rows:
            writer.writerow({field: getattr(row, field) for field in fields})


def export_result(result, output_dir: str, config: dict):
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    write_csv(
        output / config["output"]["formulas_file"],
        result.formulas,
        [
            "sheet",
            "column",
            "cell",
            "original_formula",
            "final_formula",
        ],
    )

    write_csv(
        output / config["output"]["dependencies_file"],
        result.dependencies,
        [
            "source_sheet",
            "source_cell",
            "source_column",
            "target_sheet",
            "target_cell",
            "target_column",
        ],
    )

    write_csv(
        output / config["output"]["issues_file"],
        result.issues,
        [
            "sheet",
            "cell",
            "formula",
            "reference",
            "message",
        ],
    )
