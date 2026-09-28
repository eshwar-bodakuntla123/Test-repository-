from openpyxl import load_workbook
from openpyxl.utils import get_column_letter


class WorkbookIndex:
    """
    Indexes sheet columns so a cell reference such as B5 can be resolved
    to the business header in column B.
    """

    def __init__(self, workbook, header_rows: dict, sanitizer):
        self.workbook = workbook
        self.header_rows = header_rows
        self.sanitizer = sanitizer
        self.headers: dict[str, dict[int, str]] = {}
        self._build()

    def _header_row(self, sheet_name: str) -> int:
        return int(
            self.header_rows.get(
                sheet_name,
                self.header_rows.get("default", 1),
            )
        )

    def _build(self):
        for ws in self.workbook.worksheets:
            row_number = self._header_row(ws.title)
            row = ws[row_number]
            result = {}

            for cell in row:
                value = cell.value
                if value is None:
                    continue
                result[cell.column] = self.sanitizer(str(value))

            self.headers[ws.title] = result

    def column_name(self, sheet_name: str, column_number: int) -> str | None:
        return self.headers.get(sheet_name, {}).get(column_number)

    def column_name_by_letter(self, sheet_name: str, column_letter: str) -> str | None:
        from openpyxl.utils.cell import column_index_from_string
        return self.column_name(
            sheet_name,
            column_index_from_string(column_letter),
        )

    def has_sheet(self, sheet_name: str) -> bool:
        return sheet_name in self.workbook.sheetnames
