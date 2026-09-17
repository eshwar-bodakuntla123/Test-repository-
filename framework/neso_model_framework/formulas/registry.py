"""Formula registration infrastructure."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


class FormulaRegistry:
    """Registry for named, versioned model business rules."""

    def __init__(self) -> None:
        self._rules: dict[str, Callable[..., Any]] = {}

    def register(self, formula_id: str) -> Callable:
        """Register a callable under a unique formula ID."""
        def decorator(function: Callable[..., Any]) -> Callable[..., Any]:
            if formula_id in self._rules:
                raise ValueError(f"Formula already registered: {formula_id}")
            self._rules[formula_id] = function
            return function

        return decorator

    def get(self, formula_id: str) -> Callable[..., Any]:
        """Return the registered formula implementation."""
        return self._rules[formula_id]

    def list(self) -> list[str]:
        """Return registered formula IDs."""
        return sorted(self._rules)


FORMULAS = FormulaRegistry()
