"""Structured JSON logging for model runs."""

from __future__ import annotations

import json
import logging
import sys
from typing import Any


class JsonFormatter(logging.Formatter):
    """Format log records as structured JSON."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S%z"),
            "severity": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        for key in ("run_id", "model", "pipeline", "task", "table"):
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value

        return json.dumps(payload, default=str)


class ContextLoggerAdapter(logging.LoggerAdapter):
    """Logger adapter that carries model execution context."""

    def __init__(self, logger: logging.Logger, context: dict[str, str]):
        super().__init__(logger, context)

    def process(self, msg: Any, kwargs: dict[str, Any]):
        extra = dict(self.extra)
        extra.update(kwargs.pop("extra", {}))
        kwargs["extra"] = extra
        return msg, kwargs


def get_logger(
    name: str = "neso_model_framework",
    *,
    run_id: str | None = None,
    model: str | None = None,
    pipeline: str | None = None,
    task: str | None = None,
    table: str | None = None,
) -> ContextLoggerAdapter:
    """Create a structured logger with execution context."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
        logger.propagate = False

    logger.setLevel(logging.INFO)

    context = {
        key: value
        for key, value in {
            "run_id": run_id,
            "model": model,
            "pipeline": pipeline,
            "task": task,
            "table": table,
        }.items()
        if value is not None
    }
    return ContextLoggerAdapter(logger, context)
