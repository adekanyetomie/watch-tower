import os

DEFAULT_TARGETS = "https://tomi-og.com, https://tomi-dashboard.netlify.app, https://substack.com/@tomiiiog, https://tomi-og.com/this-page-does-not-exist, https://httpstat.us/500, https://nope.tomi-og.com"

def get_targets() -> list[str]:
    raw = os.getenv("WATCHTOWER_TARGETS", DEFAULT_TARGETS)
    return [url.strip() for url in raw.split(",") if url.strip()]

def get_interval_seconds() -> int:
    return int(os.getenv("WATCHTOWER_INTERVAL_SECONDS", "30"))

def get_timeout_seconds() -> float:
    return float(os.getenv("WATCHTOWER_TIMEOUT_SECONDS", "5"))