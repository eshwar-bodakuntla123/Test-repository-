# Excel Formula Extractor

Converts an Excel workbook containing formulas into a reusable formula configuration CSV.

## What it does

```text
Excel workbook
      |
      v
Read workbook
      |
      v
Find formula cells
      |
      v
Parse Excel references
      |
      v
Resolve B5 -> Inputs.Activity
      |
      v
Create readable final_formula
      |
      v
Generate formulas.csv
```

Example:

```excel
=IF(Inputs!B5="Y",Factors!C10*Inputs!D5,0)
```

becomes:

```text
IF(Inputs.Status = "Y", Factors.EmissionFactor * Inputs.Quantity, 0)
```

The CSV keeps both the original Excel formula and the resolved formula.

## Output

`output/formulas.csv`

Columns:

- `sheet`
- `column`
- `cell`
- `original_formula`
- `final_formula`

A second file is generated:

`output/dependencies.csv`

This is optional diagnostic information. The `final_formula` remains the main configuration field.

## Installation

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

```bash
pip install -e ".[dev]"
```

## Usage

```bash
excel-formula-extractor input.xlsx
```

or:

```bash
python -m excel_formula_extractor.cli input.xlsx
```

Custom output:

```bash
excel-formula-extractor input.xlsx --output-dir output
```

Custom config:

```bash
excel-formula-extractor input.xlsx --config config.yml
```

## Header detection

By default, the extractor assumes row 1 contains column headers.

If different sheets have different header rows, configure them:

```yaml
header_rows:
  default: 1
  Inputs: 1
  Factors: 2
  Parameters: 3
  Embedded_Calculations: 1
```

The extractor resolves:

```text
Inputs!B5
```

using column B's header from the `Inputs` sheet.

It does not use row 5 as the business column name. The row is simply the referenced data row.

## Important

This tool extracts and normalizes formulas. It does not calculate Excel formulas.

Do not execute `final_formula` with Python `eval()`.

The intended architecture is:

```text
Excel
  -> formula extraction
  -> formula configuration
  -> controlled Python/PySpark calculation engine
```

## Supported references

- `A1`
- `$A$1`
- `A$1`
- `$A1`
- `Sheet1!A1`
- `'Sheet Name'!A1`
- ranges such as `A1:B10`
- cross-sheet ranges
- common Excel functions such as `IF`, `SUM`, `SUMIFS`, `VLOOKUP`, etc. are preserved as formula text

## Limitations

Some Excel features need workbook-specific handling:

- structured table references such as `Table1[Amount]`
- external workbook links
- dynamic array/spill references
- named ranges
- formulas whose logical headers cannot be determined automatically
- merged/multi-row business headers

These are reported as unresolved references rather than silently guessed.
