from prometheus_client import Counter, Gauge, Histogram

from .models import ProbeResult

TARGET_UP = Gauge(
    "watchtower_target_up",
    "Whether the target responded successfully on the last probe (1 = up, 0 = down)",
    ["url"]
)

PROBE_DURATION = Histogram(
    "watchtower_probe_duration_seconds",
    "Time taken to probe a client",
    ["url"]
)

PROBES_TOTAL = Counter(
    "watchtower_probes_total",
    "Total probes performed",
    ["url", "outcome"]
)

def record(result: ProbeResult) -> None:
    TARGET_UP.labels(url=result.url).set(1 if result.ok else 0)

    if result.latency_ms is not None:
        PROBE_DURATION.labels(url=result.url).observe(result.latency_ms / 1000)
        
    PROBES_TOTAL.labels(
        url=result.url,
        outcome="success" if result.ok else "failure"
    ).inc()