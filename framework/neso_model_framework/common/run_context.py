"""Model run context."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import uuid


@dataclass(frozen=True)
class RunContext:
    """Immutable metadata identifying one model execution."""

    model_run_id: str
    environment: str
    started_at_utc: str

    @classmethod
    def create(cls, environment: str) -> "RunContext":
        """Create a unique model execution context."""
        return cls(
            model_run_id=str(uuid.uuid4()),
            environment=environment,
            started_at_utc=datetime.now(timezone.utc).isoformat(),
        )
