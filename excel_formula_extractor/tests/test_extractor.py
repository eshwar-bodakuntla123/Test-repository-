from pathlib import Path

from openpyxl import Workbook

from excel_formula_extractor.config import DEFAULT_CONFIG
from excel_formula_extractor.extractor import extract


def test_extracts_formula(tmp_path: Path):
    path = tmp_path / "model.xlsx"

    wb = Workbook()
    inputs = wb.active
    inputs.title = "Inputs"
    inputs["A1"] = "Account"
    inputs["B1"] = "Activity"
    inputs["B5"] = "Electricity"

    factors = wb.create_sheet("Factors")
    factors["A1"] = "Factor"
    factors["C1"] = "Emission Factor"
    factors["C10"] = 0.82

    calc = wb.create_sheet("Embedded_Calculations")
    calc["A1"] = "Account"
    calc["B1"] = "Scope1"
    calc["B2"] = "=Inputs!B5*Factors!C10"

    wb.save(path)

    result = extract(str(path), DEFAULT_CONFIG)

    assert len(result.formulas) == 1
    row = result.formulas[0]

    assert row.sheet == "Embedded_Calculations"
    assert row.column == "Scope1"
    assert row.cell == "B2"
    assert row.original_formula == "=Inputs!B5*Factors!C10"
    assert row.final_formula == "=Inputs.Activity*Factors.Emission_Factor"
