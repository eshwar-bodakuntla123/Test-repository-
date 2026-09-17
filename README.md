# NESO Strategy & Policy — Python/PySpark Model Framework

Reusable framework for the NESO Strategy & Policy portfolio of 48 models.

## Architecture

```text
React UI -> FastAPI -> Databricks Jobs -> Python/PySpark Framework -> Existing NESO Data Platform
```

`framework/` contains reusable capabilities. `models/` contains model-specific business logic.
The existing Databricks Medallion/data platform is not recreated here.

### Stack

Python 3.11.x (developer baseline 3.11.9), PySpark aligned to approved DBR, pytest, Ruff, Python Wheel,
Databricks Jobs, Declarative Automation Bundles, Azure DevOps, FastAPI and React.

### Add a model

```text
models/<model_name>/
  config.yml
  formulas/
  transformations/
  modelling/
  validation/
  outputs/
  pipeline.py
```

Do not copy the framework into each model.

### Business logic

SME-approved Excel formulas are the source of truth during migration. The included activity-factor
calculation is only a technical smoke test and must not be treated as an NESO-approved formula.

### Local

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
pip install -e .
pytest
neso-model run emissions_counting --env dev --local
```

### Production

Replace the Databricks compute/runtime placeholders with client-approved values and connect the API
service to the approved Databricks Jobs integration. Never run Spark calculations inside FastAPI workers.
