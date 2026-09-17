# NESO Emissions Architecture

## Responsibility boundary

The existing NESO/Databricks platform owns the data architecture and storage layers.

This repository owns the Python/PySpark application and modelling framework.

```text
Existing data platform
        |
        v
Python/PySpark application
        |
        +-- ingestion
        +-- validation
        +-- transformation
        +-- formulas
        +-- SME adjustments
        +-- modelling
        +-- reconciliation
        +-- output contract
        |
        v
Existing data platform / consumers
```

## Medallion

If the platform uses Bronze/Silver/Gold, the framework consumes those interfaces. It does not
duplicate the platform's ownership model.

## API/UI

React is presentation only.

FastAPI is an application/API boundary.

PySpark runs as a Databricks workload, not inside the web API process.

```text
React
  |
  v
FastAPI
  |
  +--> trigger/status
  |
  v
Databricks Jobs
  |
  v
PySpark
```

## Dashboard contract

The dashboard should consume stable, business-friendly output fields such as:

- model_run_id
- scenario_id
- forecast_version
- approval_status
- sector
- geography
- year
- metric
- unit
- value
- formula_version
- adjustment_version

Do not expose internal Spark calculation columns directly to the UI.
