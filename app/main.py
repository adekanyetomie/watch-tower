import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
import httpx

from .config import get_interval_seconds, get_targets, get_timeout_seconds
from .probe import probe_loop
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

@app.get("/status")
def status(request: Request):
    store = request.app.state.store
    return {
        "targets": len(request.app.state.targets),
        "down": store.down_count(),
        "results": store.all()
    }

@app.get("/")
def read_root():
    return {"service": "watchtower", "status": "ok"}

@app.get("/healthz")
async def health_check():
    return {"message": "ok"}