import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response, status as http_status
import httpx
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from .config import get_interval_seconds, get_targets, get_timeout_seconds
from .probe import probe_loop
from .schemas import HealthResponse, StatusResponse
from .store import ResultStore

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
        # --- startup ---
    app.state.store = ResultStore()
    app.state.targets = get_targets()
    app.state.client = httpx.AsyncClient(
        follow_redirects=True,
        timeout=get_timeout_seconds()
    )
    app.state.probe_task = asyncio.create_task(
        probe_loop(
            client=app.state.client,
            store=app.state.store,
            urls=app.state.targets,
            interval_seconds= get_interval_seconds()
        )
    )

    yield

    # --- shutdown ---
    app.state.probe_task.cancel()
    try:
        await app.state.probe_task

    except asyncio.CancelledError:
        pass

    await app.state.client.aclose()



app = FastAPI(
     title="Watchtower",
    description="Uptime monitor for my own estate",
    lifespan=lifespan
)

@app.get("/status", response_model=StatusResponse)
def get_status(request: Request):
    store = request.app.state.store
    return StatusResponse(
        targets= len(request.app.state.targets),
        down=store.down_count(),
        results= store.all()
    )

@app.get("/metrics")
def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

@app.get("/health", response_model= HealthResponse)
async def health_check(request: Request, response: Response):
    task = request.app.state.probe_task
    alive = not task.done()

    if not alive:
        response.status_code = http_status.HTTP_503_SERVICE_UNAVAILABLE
    
    return HealthResponse(
        status="ok" if alive else "probe_loop_dead",
        targets=len(request.app.state.targets),
        down=down
    )