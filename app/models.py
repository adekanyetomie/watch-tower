from datetime import datetime

from pydantic import BaseModel 

class ProbeResult(BaseModel):
    url: str
    ok: bool
    status_code: int | None = None
    latency_ms: float | None = None
    error: str | None = None
    checked_at: datetime