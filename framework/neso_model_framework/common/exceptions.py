"""Framework-specific exception hierarchy."""

class NesoFrameworkError(Exception):
    """Base class for framework errors."""


class ConfigurationError(NesoFrameworkError):
    """Raised when configuration is invalid or unavailable."""


class DataAccessError(NesoFrameworkError):
    """Raised when an input/output data operation fails."""


class DataQualityError(NesoFrameworkError):
    """Raised when a data-quality gate fails."""


class ValidationError(NesoFrameworkError):
    """Raised when model validation fails."""


class FormulaError(NesoFrameworkError):
    """Raised when a business formula cannot be evaluated."""


class AdjustmentError(NesoFrameworkError):
    """Raised when an SME adjustment is invalid."""


class ReconciliationError(NesoFrameworkError):
    """Raised when a regression/reconciliation check fails."""


class ModelExecutionError(NesoFrameworkError):
    """Raised when model orchestration fails."""
