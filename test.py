
import os
import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from databricks.sdk import WorkspaceClient

# --------------------------------------------------
# Logging
# --------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)

# --------------------------------------------------
# Configuration
# --------------------------------------------------

JOB_ID = int(os.getenv("DATABRICKS_JOB_ID", "1077717963212298"))

ALLOWED_CATALOG = "sp_transmissionmodel"
ALLOWED_SCHEMA = "default"

METADATA_TABLE = (
    "sp_transmissionmodel.default.table_keys"
)

MAX_TABLES = 20
MAX_READ_ROWS = 200
MAX_BATCH_ROWS = 5000

STATIC_DIR = Path(__file__).resolve().parent / "static"

# --------------------------------------------------
# FastAPI application
# --------------------------------------------------

app = FastAPI(
    title="NESO Metadata Driven Transmission API",
    description="Dynamic transmission data operations using Databricks",
    version="1.0.0"
)

# --------------------------------------------------
# Databricks client
# --------------------------------------------------

def get_databricks_client():
    """
    Uses Databricks Apps service-principal authentication.
    The app must have the required Job and Unity Catalog permissions.
    """
    return WorkspaceClient()


# --------------------------------------------------
# Validation helpers
# --------------------------------------------------

def validate_table_name(table_name: str):

    parts = table_name.split(".")

    if len(parts) != 3:
        raise HTTPException(
            status_code=400,
            detail="Table name must be catalog.schema.table"
        )

    catalog, schema, table = parts

    if catalog != ALLOWED_CATALOG or schema != ALLOWED_SCHEMA:
        raise HTTPException(
            status_code=403,
            detail="Access to this catalog or schema is not allowed"
        )

    for part in parts:
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", part):
            raise HTTPException(
                status_code=400,
                detail="Invalid table identifier"
            )

    return table_name


def validate_request_tables(tables):

    if not tables:
        raise HTTPException(
            status_code=400,
            detail="At least one table is required"
        )

    if len(tables) > MAX_TABLES:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {MAX_TABLES} tables per request"
        )

    total_rows = 0

    for table in tables:

        validate_table_name(table.table_name)

        total_rows += (
            len(table.records or []) +
            len(table.rows or [])
        )

    if total_rows > MAX_BATCH_ROWS:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {MAX_BATCH_ROWS} rows per request"
        )


# --------------------------------------------------
# Request models
# --------------------------------------------------

class TableOperation(BaseModel):

    table_name: str

    # INSERT
    records: Optional[List[Dict[str, Any]]] = None

    # UPDATE
    rows: Optional[List[Dict[str, Any]]] = None

    primary_keys: Optional[Dict[str, Any]] = None

    update_data: Optional[Dict[str, Any]] = None

    # READ
    columns: Optional[List[str]] = None

    filters: Optional[Dict[str, Any]] = None

    limit: Optional[int] = Field(
        default=100,
        ge=1,
        le=MAX_READ_ROWS
    )


class OperationRequest(BaseModel):

    request_id: str = Field(
        min_length=1,
        max_length=128
    )

    operation: Literal["insert", "read", "update"]

    tables: List[TableOperation]


# --------------------------------------------------
# Health endpoints
# --------------------------------------------------

@app.get("/api/health")
def health_check():

    return {
        "status": "healthy",
        "application": "NESO Transmission Platform"
    }


@app.get("/api/hello")
def hello():

    return {
        "message": "Hello from NESO FastAPI"
    }


# --------------------------------------------------
# Unity Catalog metadata endpoints
# --------------------------------------------------

@app.get("/api/catalogs")
def list_catalogs():

    try:

        client = get_databricks_client()

        catalogs = [
            item.name
            for item in client.catalogs.list()
            if item.name == ALLOWED_CATALOG
        ]

        return {"catalogs": catalogs}

    except Exception:

        logger.exception("Catalog discovery failed")

        raise HTTPException(
            status_code=502,
            detail="Unable to discover catalogs"
        )


@app.get("/api/schemas")
def list_schemas(
    catalog: str = ALLOWED_CATALOG
):

    if catalog != ALLOWED_CATALOG:
        raise HTTPException(403, "Catalog not allowed")

    try:

        client = get_databricks_client()

        schemas = [
            item.name
            for item in client.schemas.list(
                catalog_name=catalog
            )
            if item.name == ALLOWED_SCHEMA
        ]

        return {
            "catalog": catalog,
            "schemas": schemas
        }

    except Exception:

        logger.exception("Schema discovery failed")

        raise HTTPException(
            status_code=502,
            detail="Unable to discover schemas"
        )


@app.get("/api/tables")
def list_tables(
    catalog: str = ALLOWED_CATALOG,
    schema: str = ALLOWED_SCHEMA
):

    if catalog != ALLOWED_CATALOG or schema != ALLOWED_SCHEMA:
        raise HTTPException(403, "Schema not allowed")

    try:

        client = get_databricks_client()

        result = []

        for table in client.tables.list(
            catalog_name=catalog,
            schema_name=schema
        ):

            result.append({
                "table_name": table.full_name,
                "name": table.name,
                "table_type": str(table.table_type)
            })

        return {
            "catalog": catalog,
            "schema": schema,
            "tables": result
        }

    except Exception:

        logger.exception("Table discovery failed")

        raise HTTPException(
            status_code=502,
            detail="Unable to discover tables"
        )


@app.get("/api/table-schema")
def get_table_schema(table_name: str):

    validate_table_name(table_name)

    try:

        client = get_databricks_client()

        table = client.tables.get(
            full_name=table_name
        )

        columns = []

        for column in (table.columns or []):

            columns.append({
                "name": column.name,
                "type": column.type_text,
                "nullable": column.nullable
            })

        return {
            "table_name": table_name,
            "columns": columns
        }

    except Exception:

        logger.exception("Table schema retrieval failed")

        raise HTTPException(
            status_code=502,
            detail="Unable to retrieve table schema"
        )


# --------------------------------------------------
# Submit Databricks Job
# --------------------------------------------------

@app.post("/api/operations")
def submit_operation(request: OperationRequest):

    validate_request_tables(request.tables)

    # Validate operation-specific payload
    for table in request.tables:

        if request.operation == "insert":

            if not table.records:
                raise HTTPException(
                    status_code=400,
                    detail="INSERT requires records"
                )

        elif request.operation == "update":

            if not table.rows and not (
                table.primary_keys and table.update_data
            ):
                raise HTTPException(
                    status_code=400,
                    detail="UPDATE requires rows or primary_keys and update_data"
                )

    payload = request.model_dump(exclude_none=True)

    try:

        client = get_databricks_client()

        run = client.jobs.run_now(
            job_id=JOB_ID,
            notebook_params={
                "payload_json": json.dumps(payload)
            }
        )

        logger.info(
            "Submitted request %s as run %s",
            request.request_id,
            run.run_id
        )

        return {
            "request_id": request.request_id,
            "run_id": run.run_id,
            "status": "SUBMITTED"
        }

    except Exception:

        logger.exception("Job submission failed")

        raise HTTPException(
            status_code=502,
            detail="Unable to submit Databricks Job"
        )


# --------------------------------------------------
# Job status and output
# --------------------------------------------------

@app.get("/api/jobs/{run_id}")
def get_job_status(run_id: int):

    try:

        client = get_databricks_client()

        run = client.jobs.get_run(
            run_id=run_id
        )

        state = run.state

        response = {
            "run_id": run_id,
            "life_cycle_state": (
                str(state.life_cycle_state)
                if state else None
            ),
            "result_state": (
                str(state.result_state)
                if state else None
            ),
            "outputs": []
        }

        if state and str(state.life_cycle_state).endswith("TERMINATED"):

            task_runs = run.tasks or [run]

            for task in task_runs:

                try:

                    output = client.jobs.get_run_output(
                        run_id=task.run_id
                    )

                    notebook_output = output.notebook_output

                    if notebook_output and notebook_output.result:

                        try:
                            parsed = json.loads(
                                notebook_output.result
                            )

                            response["outputs"].append(parsed)

                        except json.JSONDecodeError:

                            response["outputs"].append({
                                "raw_output": notebook_output.result
                            })

                except Exception:

                    logger.exception(
                        "Unable to retrieve task output"
                    )

        return response

    except Exception:

        logger.exception("Job status retrieval failed")

        raise HTTPException(
            status_code=502,
            detail="Unable to retrieve Job status"
        )


# --------------------------------------------------
# React frontend
# --------------------------------------------------

if STATIC_DIR.exists() and (STATIC_DIR / "index.html").exists():

    app.mount(
        "/",
        StaticFiles(
            directory=str(STATIC_DIR),
            html=True
        ),
        name="frontend"
    )

else:

    logger.warning(
        "React static directory not found: %s",
        STATIC_DIR
    )
