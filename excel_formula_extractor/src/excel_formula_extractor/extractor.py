from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.utils.cell import coordinate_from_string, column_index_from_string

from .config import header_row_for
from .models import (
    DependencyRecord,
    ExtractionResult,
    FormulaRecord,
    IssueRecord,
)
from .naming import sanitize_name
from .parser import resolve_formula
from .workbook import WorkbookIndex


def load_formula_workbook(path: str):
    # data_only=False is essential: we need formulas, not cached values.
    return load_workbook(path, data_only=False)


def extract(path: str, config: dict) -> ExtractionResult:
    wb = load_formula_workbook(path)

    sanitizer = sanitize_name if config["options"].get("sanitize_names", True) else str
    index = WorkbookIndex(
        wb,
        config["header_rows"],
        sanitizer,
    )

    result = ExtractionResult()

    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                value = cell.value

                if not (isinstance(value, str) and value.startswith("=")):
                    continue

                column_header = index.column_name(ws.title, cell.column)
                if not column_header:
                    column_header = get_column_letter(cell.column)

                final_formula, refs, unresolved = resolve_formula(
                    value,
                    ws.title,
                    index,
                )

                result.formulas.append(
                    FormulaRecord(
                        sheet=ws.title,
                        column=column_header,
                        cell=cell.coordinate,
                        original_formula=value,
                        final_formula=final_formula,
                    )
                )

                for ref in refs:
                    # Resolve the target cell's business column.
                    target_column = ref.source_column or ""

                    result.dependencies.append(
                        DependencyRecord(
                            source_sheet=ref.sheet,
                            source_cell=ref.start_cell,
                            source_column=target_column,
                            target_sheet=ws.title,
                            target_cell=cell.coordinate,
                            target_column=column_header,
                        )
                    )

                for token in unresolved:
                    result.issues.append(
                        IssueRecord(
                            sheet=ws.title,
                            cell=cell.coordinate,
                            formula=value,
                            reference=token,
                            message=(
                                "Reference could not be resolved to a business "
                                "column header. Check header_rows or workbook structure."
                            ),
                        )
                    )

    return result
