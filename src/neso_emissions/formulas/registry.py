from __future__ import annotations

from collections.abc import Callable
from typing import Any


class FormulaRegistry:
    """Registry of named SME/Excel reverse-engineered business rules."""

    def __init__(self) -> None:
        self._rules: dict[str, Callable[..., Any]] = {}

    def register(self, formula_id: str):
        def decorator(function: Callable[..., Any]):
            if formula_id in self._rules:
                raise ValueError(f"Formula already registered: {formula_id}")
            self._rules[formula_id] = function
            return function

        return decorator

    def get(self, formula_id: str) -> Callable[..., Any]:
        return self._rules[formula_id]

    def list(self) -> list[str]:
        return sorted(self._rules)


FORMULAS = FormulaRegistry()
