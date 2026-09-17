from __future__ import annotations

from dataclasses import dataclass
from pyspark.sql import DataFrame
from pyspark.sql import functions as F


@dataclass(frozen=True)
class CheckResult:
    name: str
    passed: bool
    details: str


def no_nulls(df: DataFrame, columns: list[str]) -> CheckResult:
    if not columns:
        return CheckResult("no_nulls", True, "no columns supplied")

    values = df.agg(
        *[F.sum(F.col(c).isNull().cast("int")).alias(c) for c in columns]
    ).first()

    bad = {c: values[c] for c in columns if values[c] and values[c] > 0}

    return CheckResult(
        "no_nulls",
        not bad,
        str(bad) if bad else "no nulls",
    )


def unique_key(df: DataFrame, keys: list[str]) -> CheckResult:
    if not keys:
        return CheckResult("unique_key", True, "no key supplied")

    total = df.count()
    distinct = df.select(*keys).dropDuplicates().count()

    return CheckResult(
        "unique_key",
        total == distinct,
        f"rows={total}, unique_keys={distinct}",
    )


def assert_passed(results: list[CheckResult]) -> None:
    failures = [result for result in results if not result.passed]

    if failures:
        raise ValueError(
            "DQ gate failed: "
            + "; ".join(f"{r.name}: {r.details}" for r in failures)
        )
