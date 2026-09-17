# NESO Emissions Counting Platform

A production-oriented starter repository for the NESO Strategy & Policy Emissions Counting model.

## Final architecture

```text
React UI
   |
   v
FastAPI API
   |
   +---- model run/status/adjustment APIs
   |
   v
Databricks Jobs
   |
   v
Python + PySpark Model Engine
   |
   +-- ingestion
   +-- validation
   +-- transformations
   +-- SME formula registry
   +-- SME adjustment workflow
   +-- modelling
   +-- reconciliation
   +-- output contract
   |
   v
Existing NESO Databricks / Medallion data platform
```

### Technology

- Python 3.11.x; current developer baseline: 3.11.9
- PySpark, version aligned to the approved Databricks Runtime
- Databricks
- Delta / Unity Catalog where provided by the platform
- Lightweight internal NESO Python/PySpark framework
- pytest
- Ruff
- Python Wheel
- Databricks Jobs
- Databricks Declarative Automation Bundles
- Azure DevOps
- FastAPI for the optional application/API layer
- React for the optional UI layer

## Important scope boundary

The existing NESO data platform owns the Medallion/data architecture. This repository does not recreate
Bronze/Silver/Gold as Python framework directories.

This repository owns the Python/PySpark application and business-processing layer.

## Reverse engineering rule

SME formulas are the source of truth for business logic during migration. Do not invent or silently
simplify formulas.

For every migrated calculation, record:

- formula ID
- business description
- source inputs
- units
- factors/lookups
- assumptions
- scenario behaviour
- Excel reference
- formula version
- SME owner
- approval status
- expected regression outputs

Use `src/neso_emissions/formulas/` for named, testable rules.

## SME adjustment rule

Never overwrite source/canonical data to represent an SME adjustment.

Use a separate adjustment dataset with:

- model_run_id
- scenario_id
- business key
- old_value
- new_value
- reason
- adjusted_by
- adjusted_at
- adjustment_version
- approval_status

Then calculate a deterministic adjusted dataset.

## Dashboard/UI rule

React should consume the API/output contract. It should not call Spark directly.

```text
React -> FastAPI -> Databricks/model results
```

Long-running model calculations should be asynchronous:

```text
POST /api/v1/model-runs
        |
        v
Databricks Job
        |
        v
status/result persistence
        |
        v
GET /api/v1/model-runs/{id}
```

## Local setup

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
pip install -e .
pytest
neso-emissions run --env dev
```

For the API:

```powershell
uvicorn api.neso_api.main:app --reload
```

The API skeleton is intentionally platform-neutral. Connect its service layer to the approved
Databricks job trigger/status mechanism once the client integration is known.

For React:

```powershell
cd ui
npm install
npm run dev
```

## Production flow

```text
Developer
  |
  v
Azure DevOps Git
  |
  +-- Ruff
  +-- pytest
  +-- build wheel
  +-- validate bundle
  |
  v
Databricks Bundle
  |
  v
Databricks Job
  |
  v
Emissions Counting
  |
  +-- validation
  +-- formulas
  +-- adjustments
  +-- calculations
  +-- reconciliation
  |
  v
Published model outputs
  |
  v
FastAPI
  |
  v
React UI
```

## First implementation principle

Use Emissions Counting as the reference model. Once the framework is proven, the same contracts can
be used by the remaining models without copying framework code.

Do not build 48 bespoke frameworks.
