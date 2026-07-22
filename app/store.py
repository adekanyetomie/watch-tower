from probe import ProbeResult

class ResultStore:
    def __init__(self) -> None:
        self._results: dict[str, ProbeResult] = {}

    def update(self, result: ProbeResult) -> None:
        self._results[result.url] = result

    def get(self, url: str) -> ProbeResult | None:
        return self._results.get(url)

    def all(self) -> list[ProbeResult]:
        return list(self._results.values())