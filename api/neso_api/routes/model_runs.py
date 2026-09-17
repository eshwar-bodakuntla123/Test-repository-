from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/model-runs", tags=["model-runs"])

_RUNS: dict[str, dict] = {}


class ModelRunRequest(BaseModel):
    model: str = Field(default="emissions_counting")
    environment: str = Field(default="dev")
    scenario_id: str = Field(default="BASE")


@router.post("", status_code=202)
def create_model_run(request: ModelRunRequest):
    run_id = str(uuid4())

    _RUNS[run_id] = {
        "run_id": run_id,
        "model": request.model,
        "environment": request.environment,
        "scenario_id": request.scenario_id,
        "status": "SUBMITTED",
    }

    # Integration point:
    # trigger the approved Databricks Job here.
    # Do not run Spark inside the FastAPI process.

    return _RUNS[run_id]


@router.get("/{run_id}")
def get_model_run(run_id: str):
    if run_id not in _RUNS:
        raise HTTPException(status_code=404, detail="Run not found")

    return _RUNS[run_id]
