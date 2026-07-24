from pydantic import BaseModel

from .models import ProbeResult


class StatusResponse(BaseModel):
    targets: int
    down: int
    results: list[ProbeResult]

class HealthResponse(BaseModel):
    status: str
    targets: int
    down: int
