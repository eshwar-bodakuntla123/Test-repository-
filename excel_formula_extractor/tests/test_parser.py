from openpyxl import Workbook

from excel_formula_extractor.parser import resolve_formula
from excel_formula_extractor.workbook import WorkbookIndex
from excel_formula_extractor.naming import sanitize_name


def build_index():
    wb = Workbook()
    ws = wb.active
    ws.title = "Inputs"
    ws["A1"] = "Account"
    ws["B1"] = "Activity"
    ws["C1"] = "Quantity"

    factors = wb.create_sheet("Factors")
    factors["A1"] = "Factor"
    factors["B1"] = "Unit"
    factors["C1"] = "Emission Factor"

    calc = wb.create_sheet("Embedded_Calculations")
    calc["A1"] = "Account"
    calc["B1"] = "Scope1"
    calc["C1"] = "Scope2"

    return WorkbookIndex(
        wb,
        {"default": 1},
        sanitize_name,
    )


def test_cross_sheet_resolution():
    index = build_index()

    final, refs, unresolved = resolve_formula(
        '=Inputs!B5*Factors!C10',
        "Embedded_Calculations",
        index,
    )

    assert final == "=Inputs.Activity*Factors.Emission_Factor"
    assert not unresolved
    assert len(refs) == 2


def test_same_sheet_resolution():
    index = build_index()

    final, refs, unresolved = resolve_formula(
        '=B2+C2',
        "Embedded_Calculations",
        index,
    )

    assert final == "=Embedded_Calculations.Scope1+Embedded_Calculations.Scope2"
    assert not unresolved
