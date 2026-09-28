import re
from dataclasses import dataclass
from openpyxl.formula import Tokenizer
from openpyxl.utils.cell import range_boundaries


# A1-style reference, optionally with a sheet prefix.
# Handles quoted sheet names such as 'Emission Factors'!B5.
CELL_REF_RE = re.compile(
    r"""
    ^
    (?:
        (?P<sheet>
            '(?:[^']|'')+'
            |
            [A-Za-z_][A-Za-z0-9_.]*
        )
        !
    )?
    (?P<cell>\$?[A-Z]{1,3}\$?[1-9][0-9]*)
    $
    """,
    re.VERBOSE,
)

RANGE_REF_RE = re.compile(
    r"""
    ^
    (?:
        (?P<sheet>
            '(?:[^']|'')+'
            |
            [A-Za-z_][A-Za-z0-9_.]*
        )
        !
    )?
    (?P<start>\$?[A-Z]{1,3}\$?[1-9][0-9]*)
    :
    (?P<end>\$?[A-Z]{1,3}\$?[1-9][0-9]*)
    $
    """,
    re.VERBOSE,
)


@dataclass(frozen=True)
class ResolvedReference:
    original: str
    sheet: str
    start_cell: str
    end_cell: str | None
    resolved: str
    source_column: str | None


def unquote_sheet(sheet: str) -> str:
    if sheet.startswith("'") and sheet.endswith("'"):
        return sheet[1:-1].replace("''", "'")
    return sheet


def strip_dollar(cell: str) -> str:
    return cell.replace("$", "")


def parse_reference(token: str, current_sheet: str):
    token = token.strip()

    m = CELL_REF_RE.match(token)
    if m:
        sheet = unquote_sheet(m.group("sheet")) if m.group("sheet") else current_sheet
        return sheet, strip_dollar(m.group("cell")), None

    m = RANGE_REF_RE.match(token)
    if m:
        sheet = unquote_sheet(m.group("sheet")) if m.group("sheet") else current_sheet
        return sheet, strip_dollar(m.group("start")), strip_dollar(m.group("end"))

    return None


def resolve_cell(sheet, cell, index, separator="."):
    from openpyxl.utils.cell import coordinate_from_string

    column, _row = coordinate_from_string(cell)
    from openpyxl.utils.cell import column_index_from_string

    col_index = column_index_from_string(column)
    name = index.column_name(sheet, col_index)

    if name:
        return f"{sheet}{separator}{name}", name

    return None, None


def resolve_reference(token: str, current_sheet: str, index) -> ResolvedReference | None:
    parsed = parse_reference(token, current_sheet)
    if not parsed:
        return None

    sheet, start, end = parsed

    if not index.has_sheet(sheet):
        return ResolvedReference(
            token, sheet, start, end, token, None
        )

    start_resolved, start_column = resolve_cell(sheet, start, index)

    if not start_resolved:
        return ResolvedReference(
            token, sheet, start, end, token, None
        )

    if end:
        end_resolved, end_column = resolve_cell(sheet, end, index)
        if not end_resolved:
            return ResolvedReference(
                token, sheet, start, end, token, start_column
            )

        # Represent a range as Sheet.StartColumn:Sheet.EndColumn.
        resolved = f"{start_resolved}:{end_resolved}"
        return ResolvedReference(
            token, sheet, start, end, resolved, start_column
        )

    return ResolvedReference(
        token, sheet, start, None, start_resolved, start_column
    )


def extract_formula_tokens(formula: str):
    """
    Return RANGE operands from an Excel formula.

    Tokenizer lets us avoid replacing text inside string literals.
    """
    tokenizer = Tokenizer(formula)

    for item in tokenizer.items:
        if item.type == "OPERAND" and item.subtype == "RANGE":
            yield item.value


def resolve_formula(formula: str, current_sheet: str, index):
    """
    Replace only A1-style RANGE operands with resolved business references.
    Return:
        final_formula, resolved_refs, unresolved_tokens
    """
    tokenizer = Tokenizer(formula)
    output = []
    refs = []
    unresolved = []

    for item in tokenizer.items:
        value = item.value

        if item.type == "OPERAND" and item.subtype == "RANGE":
            resolved = resolve_reference(value, current_sheet, index)

            if resolved:
                refs.append(resolved)

                # Only replace references that we can resolve.
                if resolved.resolved != value:
                    value = resolved.resolved
                elif CELL_REF_RE.match(value) or RANGE_REF_RE.match(value):
                    unresolved.append(value)

        output.append(value)

    final = "".join(output)
    if formula.startswith("=") and not final.startswith("="):
        final = "=" + final
    return final, refs, unresolved
