# Python Standards Compliance

## 1. Modularisation

Business logic is separated from orchestration and reusable framework capabilities.

## 2. Logging

Use `get_logger()` from `common.logging`. Logs are JSON and carry:

- timestamp
- severity
- run_id
- model
- pipeline
- task
- table when available

## 3. Error handling

Use framework exception classes. Never silently swallow exceptions.

## 4. Configuration

Use typed settings loaded from environment configuration. Never hard-code credentials,
environment-specific paths or managed table names in business logic.

## 5. Secrets

Use the `SecretProvider` abstraction and the client's approved secret manager.

## 6. Type hints

Shared/public functions use Python type annotations.

## 7. Documentation

Shared/public functions require docstrings.

## 8. Testing

pytest is required. CI enforces the agreed coverage threshold.

## 9. Dependencies

Dependencies are centrally declared. Exact production versions must be governed by the
client dependency process and approved DBR compatibility.

## 10. Pandas/NumPy

Use Spark for distributed datasets. Pandas/NumPy are appropriate only for bounded,
explicitly approved in-memory workloads.

## 11. UDFs

Prefer Spark SQL/native functions. A UDF requires technical justification and review.

## 12. Code quality

Ruff lint and formatting are enforced in CI.

## 13. CI

Azure DevOps runs lint, format check, tests, coverage and wheel build before deployment.
