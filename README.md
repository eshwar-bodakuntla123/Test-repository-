# NESO Strategy & Policy — Standards-Compliant Python/PySpark Framework

Reusable framework for the NESO Strategy & Policy portfolio of 48 models.

## Client Python standards covered

| Standard | Implementation |
|---|---|
| Modularisation | `framework/` reusable capabilities; `models/` business logic; orchestration separated |
| Logging | Structured JSON logging with run ID, model, pipeline, task, table and severity |
| Error handling | Typed framework exception hierarchy; no silent exception blocks |
| Configuration | YAML + typed settings; no environment/table/path hard-coding in model logic |
| Secrets | Secret-provider abstraction; no credentials in source control |
| Type hints | Shared/public framework functions are type annotated |
| Documentation | Public/shared functions have docstrings |
| Testing | pytest, coverage gate, framework/model tests and regression structure |
| Dependencies | Central requirements + constraints; production versions must align to approved DBR |
| Pandas/NumPy | Not used for distributed datasets; Spark is the default processing engine |
| UDF usage | Spark native functions preferred; no Python UDF in starter |
| Code quality | Ruff lint + format + CI |
| CI | Azure DevOps pipeline validates lint, formatting, tests, coverage and package build |

## Architecture

```text
React UI
   |
FastAPI
   |
Databricks Jobs
   |
Python Wheel
   |
NESO Model Framework
   |
Model-specific implementation
   |
Existing NESO Databricks / Medallion platform
```

The existing NESO data platform owns Bronze/Silver/Gold. This application framework consumes approved
data interfaces and does not recreate platform ownership.

## Repository layout

```text
framework/       reusable framework
models/          one implementation per business model
jobs/            Databricks entry points
config/          environment/model configuration and contracts
api/             FastAPI boundary
ui/              React dashboard
tests/           framework + model tests
resources/       Databricks resources
docs/            governance and development standards
scripts/         local developer helpers
```

## Local development

Python 3.11.9 is the current AVD developer baseline.

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
pip install -e .
ruff check framework models tests api
ruff format --check framework models tests api
pytest --cov=framework --cov=models --cov-fail-under=80
neso-model run emissions_counting --env dev --local
```

Exact production PySpark must be aligned with the approved Databricks Runtime. Do not choose a
production Spark/PySpark version independently of the client's DBR.

## Formula governance

Actual NESO formulas must come from SME-approved Excel reverse engineering. The included
activity × factor rule is only a technical smoke test and must not be treated as an approved
NESO formula.

Each business rule should have a formula ID, source/reference, units, assumptions, scenario
behaviour, version, owner, approval status and regression test.

## Secrets

Use the approved enterprise secret manager/Databricks secret mechanism through the secret-provider
abstraction. Never commit tokens, passwords, client credentials, connection strings or `.env` files.

## Model extensibility

Add a new model under `models/<model_name>/`; do not copy the framework.





neso-strategy-policy/
│
├── framework/              ← COMMON, reusable across 48 models
│   └── neso_model_framework/
│
├── models/                 ← BUSINESS LOGIC
│   ├── emissions_counting/
│   ├── model_02/
│   ├── model_03/
│   └── ...
│
├── jobs/                   ← Databricks execution
├── config/                 ← Environment/model configuration
├── resources/              ← Databricks resources
├── api/                    ← FastAPI
├── ui/                     ← React
├── tests/                  ← Framework + model tests
├── docs/                   ← Standards/governance
├── scripts/
│
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── databricks.yml
└── azure-pipelines.yml