"""Reusable data-quality checks."""

from __future__ import annotations

from dataclasses import dataclass

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from neso_model_framework.common.exceptions import DataQualityError


@dataclass(frozen=True)
class CheckResult:
    """Result of a single data-quality check."""

    name: str
    passed: bool
    details: str


def required_columns(df: DataFrame, columns: list[str]) -> CheckResult:
    """Check that all required columns exist."""
    missing = [column for column in columns if column not in df.columns]
    return CheckResult(
        name="required_columns",
        passed=not missing,
        details=str(missing) if missing else "ok",
    )


def no_nulls(df: DataFrame, columns: list[str]) -> CheckResult:
    """Check that selected columns contain no null values."""
    if not columns:
        return CheckResult("no_nulls", True, "no columns supplied")

    row = df.agg(
        *[F.sum(F.col(column).isNull().cast("int")).alias(column) for column in columns]
    ).first()

    bad = {column: row[column] for column in columns if row[column] and row[column] > 0}
    return CheckResult("no_nulls", not bad, str(bad) if bad else "ok")


def unique_key(df: DataFrame, keys: list[str]) -> CheckResult:
    """Check uniqueness of a business key."""
    if not keys:
        raise DataQualityError("At least one key column is required.")

    total = df.count()
    unique = df.select(*keys).dropDuplicates().count()
    return CheckResult("unique_key", total == unique, f"rows={total}, unique={unique}")


def assert_passed(results: list[CheckResult]) -> None:
    """Raise a typed DQ error when any critical check fails."""
    failures = [result for result in results if not result.passed]

    if failures:
        details = "; ".join(f"{item.name}: {item.details}" for item in failures)
        raise DataQualityError(f"DQ gate failed: {details}")
