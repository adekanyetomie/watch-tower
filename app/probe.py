import asyncio
import time 
from datetime import datetime, timezone
import httpx

from .metrics import record
from .models import ProbeResult


async def probe(client: httpx.AsyncClient, url: str) -> ProbeResult: 
    start = time.perf_counter()
    try:
        response = await client.get(url)
    except httpx.RequestError as exc: 
        elapsed_time = (time.perf_counter() - start) * 1000
        return ProbeResult(
            url=url,
            ok=False,
            latency_ms=round(elapsed_time, 1),
            error=type(exc).__name__,
            checked_at= datetime.now(timezone.utc)          
        )

    elapsed_time = (time.perf_counter() - start) * 1000
    return ProbeResult(
            url=url,
            ok=response.is_success,
            status_code=response.status_code,
            latency_ms=round(elapsed_time, 1),
            checked_at= datetime.now(timezone.utc)          
        )

async def probe_all(client: httpx.AsyncClient, urls: list[str]) -> list[ProbeResult]:
    return await asyncio.gather(*(probe(client, u) for u in urls))


import logging

logger = logging.getLogger(__name__)

async def probe_loop(
    client: httpx.AsyncClient,
    store,
    urls: list[str],
    interval_seconds: int
) -> None:
    while True:
        try:
            results = await probe_all(client, urls)
            for result in results:
                store.update(result)
                record(result)
            logger.info("probed %d targets, %d down", len(results), store.down_count())

        except asyncio.CancelledError:
            logger.info("probe loop cancelled")
            raise

        except Exception:
            logger.exception("probe cycle failed")

        await asyncio.sleep(interval_seconds)


# Demo runner

async def _demo():
    from store import ResultStore
    
    urls = [
        "https://tomi-og.com",
        "https://tomi-dashboard.netlify.app",
        "https://substack.com/@tomiiiog"
        "https://httpstat.us/500",              # answers, but unhappily
        "https://nope.tomi-og.com",             # unreachable
    ]

    store = ResultStore()

    async with httpx.AsyncClient(follow_redirects=True, timeout=5.0) as client:
        results = await probe_all(client, urls)
    
    for r in results:
        print(store.update(r))

  # read back out of the store, not the probe results directly
    for r in store.all():
        print(r.model_dump_json())


if __name__ == "__main__":
    asyncio.run(_demo())

