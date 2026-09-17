# Architecture

## Core boundary

```text
Existing NESO Databricks / Medallion
                |
                v
       framework/ingestion
                |
                v
       framework/validation
                |
                v
    model-specific transformations
                |
                v
      SME-approved formulas
                |
                v
          model results
                |
                v
        reconciliation
                |
                v
        output contract
```

The application does not recreate Bronze/Silver/Gold.

## One framework, many models

```text
framework/
    common reusable capabilities
    ingestion
    validation
    adjustments
    formulas registry
    reconciliation
    outputs
    orchestration

models/
    emissions_counting/
    model_02/
    ...
    model_48/
```

## API/UI

React is presentation only.

FastAPI is an API/application boundary.

Databricks Jobs run Spark workloads.

Never run large Spark workloads inside FastAPI request workers.
