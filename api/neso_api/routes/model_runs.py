from uuid import uuid4

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/model-runs", tags=["model-runs"])
runs: dict[str, dict[str, str]] = {}


class ModelRunRequest(BaseModel):
    """Request to start a model run."""

    model: str = Field(default="emissions_counting")
    environment: str = Field(default="prod")
    scenario_id: str = Field(default="BASE")


@router.post("", status_code=202)
def create_run(request: ModelRunRequest) -> dict[str, str]:
    """Submit a model run.

    Production implementation should trigger the approved Databricks Job.
    Spark must not execute inside FastAPI workers.
    """
    run_id = str(uuid4())
    result = {
        "run_id": run_id,
        "model": request.model,
        "environment": request.environment,
        "scenario_id": request.scenario_id,
        "status": "SUBMITTED",
    }
    runs[run_id] = result
    return result


@router.get("/{run_id}")
def get_run(run_id: str) -> dict[str, str]:
    """Return model run status."""
    return runs.get(run_id, {"run_id": run_id, "status": "NOT_FOUND"})
