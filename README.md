Python

# ============================================================
# NESO - DYNAMIC TABLE PROCESSING FRAMEWORK
# Azure Databricks + Unity Catalog + Delta Lake
#
# Operations:
#   insert : single or multiple records
#   update : single or multiple records, partial updates
#   read   : dynamic columns and equality filters
#
# Supports:
#   multiple tables in one request
#   dynamic schema discovery
#   primary-key lookup from table_keys
#   per-table results and explicit failure reporting
#
# No DELETE operation.
# ============================================================

import json
import re
from decimal import Decimal
from delta.tables import DeltaTable
from pyspark.sql import functions as F

# ------------------------------------------------------------
# 1. CONFIGURATION
# ------------------------------------------------------------

ALLOWED_SCHEMAS = {
    "sp_transmissionmodel.default"
}

KEY_METADATA_TABLE = (
    "sp_transmissionmodel.default.table_keys"
)

MAX_READ_ROWS = 200
MAX_TABLES_PER_REQUEST = 20
MAX_BATCH_ROWS = 5000

# ------------------------------------------------------------
# 2. READ JOB PARAMETER
# ------------------------------------------------------------

try:
    raw_payload = dbutils.widgets.get("payload_json")
except Exception:
    dbutils.widgets.text("payload_json", "{}")
    raw_payload = dbutils.widgets.get("payload_json")

if not raw_payload or not raw_payload.strip():
    raise ValueError("Request payload cannot be empty")

try:
    payload = json.loads(raw_payload)
except json.JSONDecodeError as exc:
    raise ValueError(
        f"Invalid JSON payload: {exc}"
    )

# ------------------------------------------------------------
# 3. REQUEST VALIDATION
# ------------------------------------------------------------

if not isinstance(payload, dict):
    raise ValueError("Payload must be a JSON object")

request_id = payload.get("request_id", "UNKNOWN")

operation = payload.get("operation")

if operation not in ("insert", "update", "read"):
    raise ValueError(
        "operation must be insert, update or read"
    )

tables = payload.get("tables")

if not isinstance(tables, list) or not tables:
    raise ValueError(
        "tables must be a non-empty array"
    )

if len(tables) > MAX_TABLES_PER_REQUEST:
    raise ValueError("Too many tables in one request")

# ------------------------------------------------------------
# 4. TABLE NAME VALIDATION
# ------------------------------------------------------------

def validate_table_name(table_name):

    if not isinstance(table_name, str):
        raise ValueError("Invalid table name")

    parts = table_name.split(".")

    if len(parts) != 3:
        raise ValueError(
            "Table name must be catalog.schema.table"
        )

    if not all(
        re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", p)
        for p in parts
    ):
        raise ValueError("Invalid table identifier")

    schema_name = ".".join(parts[:2])

    if schema_name not in ALLOWED_SCHEMAS:
        raise PermissionError(
            f"Schema is not allowed: {schema_name}"
        )

    if not spark.catalog.tableExists(table_name):
        raise ValueError(
            f"Table does not exist: {table_name}"
        )

    return table_name

# ------------------------------------------------------------
# 5. DYNAMIC SCHEMA DISCOVERY
# ------------------------------------------------------------

def get_table_schema(table_name):

    return spark.table(table_name).schema


def validate_columns(columns, schema, label):

    actual_columns = {
        field.name for field in schema.fields
    }

    invalid = set(columns) - actual_columns

    if invalid:
        raise ValueError(
            f"Invalid {label} columns: {sorted(invalid)}"
        )


# ------------------------------------------------------------
# 6. PRIMARY KEY METADATA
# ------------------------------------------------------------

def get_primary_keys(table_name, schema):

    metadata = spark.table(
        KEY_METADATA_TABLE
    )

    matches = (
        metadata
        .filter(
            (F.col("table_name") == table_name)
            & (F.col("enabled") == True)
        )
        .collect()
    )

    if len(matches) != 1:
        raise ValueError(
            "Expected exactly one enabled key mapping "
            f"for {table_name}; found {len(matches)}"
        )

    keys = matches[0]["key_columns"]

    if not keys:
        raise ValueError("Primary-key mapping is empty")

    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate primary-key columns")

    validate_columns(keys, schema, "primary-key")

    return keys


# ------------------------------------------------------------
# 7. BUILD SOURCE DATAFRAME USING TARGET COLUMN TYPES
# ------------------------------------------------------------

def build_source_dataframe(records, target_schema, columns):

    fields = [
        target_schema[name]
        for name in columns
    ]

    source_schema = type(target_schema)(fields)

    source_rows = []

    for record in records:
        values = []

        for field in fields:
            value = record.get(field.name)

            if value is not None:
                if field.dataType.typeName() == "decimal":
                    value = Decimal(str(value))

            values.append(value)

        source_rows.append(tuple(values))

    return spark.createDataFrame(
        source_rows,
        schema=source_schema
    )


# ------------------------------------------------------------
# 8. INSERT OPERATION
# ------------------------------------------------------------

def process_insert(table_name, table_spec, schema):

    records = table_spec.get("records")

    if not isinstance(records, list) or not records:
        raise ValueError(
            "Insert requires a non-empty records array"
        )

    if len(records) > MAX_BATCH_ROWS:
        raise ValueError("Insert batch exceeds row limit")

    columns = set()

    for record in records:

        if not isinstance(record, dict) or not record:
            raise ValueError("Each record must be a non-empty object")

        columns.update(record.keys())

    validate_columns(columns, schema, "insert")

    target_fields = {
        field.name: field
        for field in schema.fields
    }

    missing_required = []

    for field in schema.fields:

        if not field.nullable:
            if any(
                field.name not in record
                or record[field.name] is None
                for record in records
            ):
                missing_required.append(field.name)

    if missing_required:
        raise ValueError(
            "Missing non-nullable columns: "
            f"{missing_required}"
        )

    # Every record is aligned to the actual target schema.
    # Omitted nullable columns are set to NULL.
    aligned_records = []

    for record in records:
        aligned_records.append({
            field.name: record.get(field.name)
            for field in schema.fields
        })

    all_columns = [
        field.name for field in schema.fields
    ]

    source_df = build_source_dataframe(
        aligned_records,
        schema,
        all_columns
    )

    (
        source_df
        .write
        .format("delta")
        .mode("append")
        .saveAsTable(table_name)
    )

    return {
        "status": "success",
        "inserted_rows": len(records)
    }


# ------------------------------------------------------------
# 9. UPDATE OPERATION - PARTIAL UPDATE
# ------------------------------------------------------------

def process_update(table_name, table_spec, schema):

    primary_keys = get_primary_keys(
        table_name,
        schema
    )

    # Supports multiple rows.
    # Also supports the earlier single-row format.
    rows = table_spec.get("rows")

    if rows is None:

        if (
            "primary_keys" in table_spec
            and "update_data" in table_spec
        ):
            rows = [{
                "primary_keys": table_spec["primary_keys"],
                "update_data": table_spec["update_data"]
            }]
        else:
            raise ValueError(
                "Update requires rows or primary_keys "
                "and update_data"
            )

    if not isinstance(rows, list) or not rows:
        raise ValueError(
            "Update rows must be a non-empty array"
        )

    if len(rows) > MAX_BATCH_ROWS:
        raise ValueError("Update batch exceeds row limit")

    target_columns = {
        field.name for field in schema.fields
    }

    update_records = []

    seen_keys = set()

    for row in rows:

        keys = row.get("primary_keys")
        updates = row.get("update_data")

        if not isinstance(keys, dict):
            raise ValueError(
                "Each row requires a primary_keys object"
            )

        if set(keys.keys()) != set(primary_keys):
            raise ValueError(
                f"Primary keys must be exactly {primary_keys}"
            )

        if any(value is None for value in keys.values()):
            raise ValueError("Primary-key values cannot be NULL")

        if not isinstance(updates, dict) or not updates:
            raise ValueError(
                "Each row requires non-empty update_data"
            )

        invalid_columns = set(updates) - target_columns

        if invalid_columns:
            raise ValueError(
                f"Unknown update columns: {invalid_columns}"
            )

        protected_columns = set(primary_keys) & set(updates)

        if protected_columns:
            raise ValueError(
                "Primary-key columns cannot be updated: "
                f"{protected_columns}"
            )

        combined = {
            **keys,
            **updates
        }

        key_signature = tuple(
            json.dumps(keys[k], sort_keys=True)
            for k in primary_keys
        )

        if key_signature in seen_keys:
            raise ValueError(
                "Duplicate primary-key values in update batch"
            )

        seen_keys.add(key_signature)

        update_records.append(combined)

    update_columns = sorted(
        set().union(
            *[
                set(row["update_data"].keys())
                for row in rows
            ]
        )
    )

    source_columns = list(
        dict.fromkeys(primary_keys + update_columns)
    )

    source_df = build_source_dataframe(
        update_records,
        schema,
        source_columns
    )

    # Prevent accidental multiple source matches.
    if source_df.count() != len(update_records):
        raise ValueError("Invalid update source row count")

    # Build a quoted key match expression.
    condition = " AND ".join(
        [
            f"t.`{key}` <=> s.`{key}`"
            for key in primary_keys
        ]
    )

    update_set = {
        column: f"s.`{column}`"
        for column in update_columns
    }

    # UPDATE MATCHED ONLY.
    # Unmatched records are NOT inserted.
    target = DeltaTable.forName(
        spark,
        table_name
    )

    (
        target.alias("t")
        .merge(
            source_df.alias("s"),
            condition
        )
        .whenMatchedUpdate(
            set=update_set
        )
        .execute()
    )

    return {
        "status": "success",
        "processed_rows": len(update_records),
        "updated_columns": update_columns,
        "primary_keys": primary_keys,
        "matched_rows": (
            target.toDF()
            .join(
                source_df.select(*primary_keys).distinct(),
                primary_keys,
                "inner"
            )
            .count()
        )
    }


# ------------------------------------------------------------
# 10. READ OPERATION
# ------------------------------------------------------------

def process_read(table_name, table_spec, schema):

    requested_columns = table_spec.get("columns")

    if not requested_columns:
        requested_columns = [
            field.name for field in schema.fields
        ]

    if not isinstance(requested_columns, list):
        raise ValueError("columns must be an array")

    if len(requested_columns) != len(set(requested_columns)):
        raise ValueError("Duplicate requested columns")

    validate_columns(
        requested_columns,
        schema,
        "read"
    )

    df = spark.table(table_name)

    filters = table_spec.get("filters", {})

    if not isinstance(filters, dict):
        raise ValueError("filters must be an object")

    validate_columns(
        filters.keys(),
        schema,
        "filter"
    )

    # Equality and NULL filters only.
    for column, value in filters.items():

        if value is None:
            df = df.filter(
                F.col(column).isNull()
            )
        else:
            df = df.filter(
                F.col(column) == F.lit(value)
            )

    limit = table_spec.get("limit", 20)

    if not isinstance(limit, int) or isinstance(limit, bool):
        raise ValueError("limit must be an integer")

    if limit < 1:
        raise ValueError("limit must be positive")

    limit = min(limit, MAX_READ_ROWS)

    result_rows = [
        row.asDict(recursive=True)
        for row in (
            df.select(*requested_columns)
            .limit(limit)
            .collect()
        )
    ]

    return {
        "status": "success",
        "columns": requested_columns,
        "rows": result_rows,
        "row_count": len(result_rows)
    }


# ------------------------------------------------------------
# 11. PROCESS MULTIPLE TABLES
# ------------------------------------------------------------

results = []

for table_spec in tables:

    table_name = table_spec.get("table_name")

    table_result = {
        "table_name": table_name,
        "operation": operation,
        "status": "failed"
    }

    try:

        if not isinstance(table_spec, dict):
            raise ValueError(
                "Each tables entry must be an object"
            )

        table_name = validate_table_name(
            table_spec.get("table_name")
        )

        schema = get_table_schema(table_name)

        if operation == "insert":

            result = process_insert(
                table_name,
                table_spec,
                schema
            )

        elif operation == "update":

            result = process_update(
                table_name,
                table_spec,
                schema
            )

        elif operation == "read":

            result = process_read(
                table_name,
                table_spec,
                schema
            )

        table_result.update(result)

        table_result["status"] = "success"

    except Exception as exc:

        table_result["status"] = "failed"
        table_result["error"] = str(exc)

    results.append(table_result)


# ------------------------------------------------------------
# 12. FINAL RESPONSE
# ------------------------------------------------------------

response = {
    "request_id": request_id,
    "operation": operation,
    "status": (
        "success"
        if all(r["status"] == "success" for r in results)
        else "failed"
    ),
    "table_results": results,
    "warning": (
        "Multi-table operations are not atomic. "
        "Review per-table results."
    )
}

response_json = json.dumps(
    response,
    default=str
)

print(response_json)

# Make the Databricks Job fail if any table failed.
if response["status"] == "failed":
    raise RuntimeError(response_json)

dbutils.notebook.exit(response_json)
