from dataclasses import dataclass
from datetime import datetime, timezone
import uuid
@dataclass(frozen=True)
class RunContext:
    model_run_id: str
    environment: str
    started_at_utc: str
    @classmethod
    def create(cls, environment: str):
        return cls(str(uuid.uuid4()), environment, datetime.now(timezone.utc).isoformat())
