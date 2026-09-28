from dataclasses import dataclass, field


@dataclass(frozen=True)
class FormulaRecord:
    sheet: str
    column: str
    cell: str
    original_formula: str
    final_formula: str


@dataclass(frozen=True)
class DependencyRecord:
    source_sheet: str
    source_cell: str
    source_column: str
    target_sheet: str
    target_cell: str
    target_column: str


@dataclass(frozen=True)
class IssueRecord:
    sheet: str
    cell: str
    formula: str
    reference: str
    message: str


@dataclass
class ExtractionResult:
    formulas: list[FormulaRecord] = field(default_factory=list)
    dependencies: list[DependencyRecord] = field(default_factory=list)
    issues: list[IssueRecord] = field(default_factory=list)
