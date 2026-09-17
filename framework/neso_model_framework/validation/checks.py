from dataclasses import dataclass
from pyspark.sql import DataFrame
from pyspark.sql import functions as F
@dataclass(frozen=True)
class CheckResult:
    name: str
    passed: bool
    details: str
def required_columns(df: DataFrame, columns: list[str]) -> CheckResult:
    missing=[c for c in columns if c not in df.columns]
    return CheckResult("required_columns", not missing, str(missing) if missing else "ok")
def no_nulls(df: DataFrame, columns: list[str]) -> CheckResult:
    row=df.agg(*[F.sum(F.col(c).isNull().cast("int")).alias(c) for c in columns]).first()
    bad={c: row[c] for c in columns if row[c] and row[c]>0}
    return CheckResult("no_nulls", not bad, str(bad) if bad else "ok")
def assert_passed(results: list[CheckResult]) -> None:
    failures=[r for r in results if not r.passed]
    if failures: raise ValueError("DQ gate failed: "+"; ".join(f"{r.name}: {r.details}" for r in failures))
