# SME Adjustments

Never overwrite canonical source data to represent an SME intervention.

Store an adjustment record containing at least:

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

Only approved adjustments are applied to model calculations.
