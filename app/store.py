from .models import ProbeResult

class ResultStore:
    def __init__(self) -> None:
        self._results: dict[str, ProbeResult] = {}

    def update(self, result: ProbeResult) -> None:
        self._results[result.url] = result

    def get(self, url: str) -> ProbeResult | None:
        return self._results.get(url)

    def all(self) -> list[ProbeResult]:
        return list(self._results.values())
    
    def down_count(self) -> int:
        return sum(1 for r in self._results.values() if not r.ok)