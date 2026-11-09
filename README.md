
import os
import json
import logging
from typing import Any, Dict, List, Literal

from fastapi import HTTPException
from pydantic import BaseModel, Field
from databricks.sdk import WorkspaceClient

logger = logging.getLogger(__name__)

JOB_ID = int(os.getenv("DATABRICKS_JOB_ID", "1077717963212298"))
ALLOWED_CATALOG = "sp_transmissionmodel"
ALLOWED_SCHEMA = "default"

def get_client():
    return WorkspaceClient()

def validate_namespace(catalog: str, schema: str):
    if catalog != ALLOWED_CATALOG or schema != ALLOWED_SCHEMA:
        raise HTTPException(
            status_code=403,
            detail="Catalog or schema is not allowed"
        )

def validate_table(table_name: str):
    parts = table_name.split(".")
    if len(parts) != 3:
        raise HTTPException(
            status_code=400,
            detail="Use catalog.schema.table"
        )

    validate_namespace(parts[0], parts[1])

    if not all(p.replace("_", "").isalnum() for p in parts):
        raise HTTPException(
            status_code=400,
            detail="Invalid table identifier"
        )

    return table_name


class TableOperation(BaseModel):
    table_name: str
    records: List[Dict[str, Any]] | None = None
    rows: List[Dict[str, Any]] | None = None
    columns: List[str] | None = None
    filters: Dict[str, Any] | None = None
    limit: int | None = Field(default=None, ge=1, le=200)
    primary_keys: Dict[str, Any] | None = None
    update_data: Dict[str, Any] | None = None


class OperationRequest(BaseModel):
    request_id: str = Field(min_length=1, max_length=128)
    operation: Literal["read", "insert", "update"]
    tables: List[TableOperation] = Field(min_length=1, max_length=20)


@app.get("/api/catalogs")
def list_catalogs():
    client = get_client()
    catalogs = [
        c.name
        for c in client.catalogs.list()
        if c.name == ALLOWED_CATALOG
    ]
    return {"catalogs": catalogs}


@app.get("/api/schemas")
def list_schemas(catalog: str = ALLOWED_CATALOG):
    if catalog != ALLOWED_CATALOG:
        raise HTTPException(403, "Catalog not allowed")

    client = get_client()
    schemas = [
        s.name
        for s in client.schemas.list(catalog_name=catalog)
        if s.name == ALLOWED_SCHEMA
    ]
    return {"schemas": schemas}


@app.get("/api/tables")
def list_tables(
    catalog: str = ALLOWED_CATALOG,
    schema: str = ALLOWED_SCHEMA
):
    validate_namespace(catalog, schema)

    client = get_client()
    tables = []

    for t in client.tables.list(
        catalog_name=catalog,
        schema_name=schema
    ):
        tables.append({
            "table_name": t.full_name,
            "name": t.name,
            "table_type": str(t.table_type)
        })

    return {"tables": tables}


@app.get("/api/table-schema")
def get_table_schema(table_name: str):
    validate_table(table_name)

    client = get_client()
    table = client.tables.get(full_name=table_name)

    return {
        "table_name": table.full_name,
        "columns": [
            {
                "name": c.name,
                "type": c.type_text,
                "nullable": c.nullable
            }
            for c in (table.columns or [])
        ]
    }


@app.post("/api/operations")
def submit_operation(request: OperationRequest):
    payload = request.model_dump(exclude_none=True)

    for table in payload["tables"]:
        validate_table(table["table_name"])

        if request.operation == "insert":
            if not table.get("records"):
                raise HTTPException(
                    400,
                    "INSERT requires non-empty records"
                )

        elif request.operation == "update":
            if not table.get("rows") and not (
                table.get("primary_keys") and table.get("update_data")
            ):
                raise HTTPException(
                    400,
                    "UPDATE requires rows or primary_keys and update_data"
                )

    try:
        client = get_client()

        run = client.jobs.run_now(
            job_id=JOB_ID,
            notebook_params={
                "payload_json": json.dumps(payload)
            }
        )

        return {
            "request_id": request.request_id,
            "run_id": run.run_id,
            "status": "SUBMITTED"
        }

    except Exception:
        logger.exception("Databricks Job submission failed")
        raise HTTPException(
            502,
            "Unable to submit Databricks Job"
        )


@app.get("/api/jobs/{run_id}")
def get_job_status(run_id: int):
    try:
        client = get_client()
        run = client.jobs.get_run(run_id=run_id)

        result = {
            "run_id": run_id,
            "life_cycle_state": (
                str(run.state.life_cycle_state)
                if run.state else None
            ),
            "result_state": (
                str(run.state.result_state)
                if run.state else None
            )
        }

        if run.state and str(run.state.life_cycle_state).endswith(
            "TERMINATED"
        ):
            task_runs = run.tasks or [run]

            outputs = []
            for task in task_runs:
                try:
                    output = client.jobs.get_run_output(
                        run_id=task.run_id
                    )
                    notebook = output.notebook_output
                    if notebook and notebook.result:
                        try:
                            outputs.append(json.loads(notebook.result))
                        except json.JSONDecodeError:
                            outputs.append({
                                "raw_output": notebook.result
                            })
                except Exception:
                    logger.exception("Unable to retrieve task output")

            result["outputs"] = outputs

        return result

    except Exception:
        logger.exception("Databricks Job status retrieval failed")
        raise HTTPException(
            502,
            "Unable to retrieve Databricks Job status"
        )
