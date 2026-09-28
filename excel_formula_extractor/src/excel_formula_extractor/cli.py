import argparse
from pathlib import Path

from .config import load_config
from .extractor import extract
from .exporter import export_result


def main():
    parser = argparse.ArgumentParser(
        description="Extract and resolve Excel formulas into CSV configuration."
    )

    parser.add_argument(
        "input",
        help="Path to the Excel .xlsx workbook.",
    )

    parser.add_argument(
        "--config",
        default="config.yml",
        help="Path to config YAML.",
    )

    parser.add_argument(
        "--output-dir",
        default="output",
        help="Output directory.",
    )

    args = parser.parse_args()

    input_path = Path(args.input)

    if not input_path.exists():
        parser.error(f"Input file does not exist: {input_path}")

    if input_path.suffix.lower() != ".xlsx":
        parser.error("Only .xlsx workbooks are supported.")

    config = load_config(args.config if Path(args.config).exists() else None)

    result = extract(str(input_path), config)
    export_result(result, args.output_dir, config)

    print(f"Formula rows: {len(result.formulas)}")
    print(f"Dependencies: {len(result.dependencies)}")
    print(f"Unresolved references: {len(result.issues)}")
    print(f"Output: {Path(args.output_dir).resolve()}")


if __name__ == "__main__":
    main()
