# Architecture

One reusable framework supports all 48 models. Model-specific business logic stays under `models/`.

```text
React -> FastAPI -> Databricks Jobs -> framework -> model implementation -> existing NESO data platform
```

Bronze/Silver/Gold remains a platform concern. This repository consumes approved data interfaces.

Framework responsibilities: configuration, ingestion, validation, transformations, adjustments,
formula registry, reconciliation, outputs and orchestration.

Model responsibilities: formulas, transformations, modelling, model-specific validation, outputs and pipeline.
