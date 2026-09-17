# FastAPI layer

This is an optional application boundary for the future React UI.

Important:
- Do not run Spark in FastAPI workers.
- Trigger Databricks Jobs for long-running model work.
- Read persisted model results through an approved data/API access layer.
- Add enterprise authentication/RBAC according to the client architecture.
