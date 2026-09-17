# Dashboard Contract

Stable fields exposed to downstream consumers should include:

- model_run_id
- scenario_id
- sector
- geography
- year
- metric
- unit
- value
- formula_version
- adjustment_version
- approval_status

The UI must not depend on internal Spark calculation columns.
