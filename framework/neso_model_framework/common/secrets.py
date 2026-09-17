"""Secret-provider abstraction.

The framework never stores credentials in source control. Production should implement
this interface with the client's approved Databricks/enterprise secret provider.
"""

from __future__ import annotations

from typing import Protocol

from neso_model_framework.common.exceptions import ConfigurationError


class SecretProvider(Protocol):
    """Interface for retrieving a secret without exposing it in source control."""

    def get_secret(self, scope: str, key: str) -> str:
        """Return a secret from the approved secret-management system."""


class EnvironmentSecretProvider:
    """Development-only provider that reads a secret from an environment variable."""

    def get_secret(self, scope: str, key: str) -> str:
        """Read a development secret from an environment variable."""
        import os

        variable = f"{scope}_{key}".upper().replace("-", "_")
        value = os.getenv(variable)

        if not value:
            raise ConfigurationError(
                f"Secret {scope}/{key} is not available in the development environment."
            )

        return value
