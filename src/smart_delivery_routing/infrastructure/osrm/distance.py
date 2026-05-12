import httpx

from smart_delivery_routing.domain.models import Location
from smart_delivery_routing.domain.ports import DistanceCalculator
from smart_delivery_routing.infrastructure.haversine import HaversineDistanceCalculator

_cache: dict[tuple, list[list[float]]] = {}


class OSRMDistanceCalculator(DistanceCalculator):
    def __init__(self, base_url: str = "http://router.project-osrm.org") -> None:
        self._base_url = base_url
        self._fallback = HaversineDistanceCalculator()

    def compute_matrix(self, locations: list[Location]) -> list[list[float]]:
        key = tuple((loc.lat, loc.lng) for loc in locations)
        if key in _cache:
            print(f"[OSRMDistanceCalculator] cache hit ({len(locations)} locations)", flush=True)
            return _cache[key]

        print(f"[OSRMDistanceCalculator] cache miss — calling OSRM ({len(locations)} locations)", flush=True)
        coords_str = ";".join(f"{loc.lng},{loc.lat}" for loc in locations)
        try:
            resp = httpx.get(
                f"{self._base_url}/table/v1/driving/{coords_str}",
                params={"annotations": "distance"},
                timeout=30.0,
            )
            resp.raise_for_status()
            data = resp.json()
            if data.get("code") != "Ok":
                raise RuntimeError(data.get("message", data.get("code")))
            matrix = [[d / 1000 for d in row] for row in data["distances"]]
            _cache[key] = matrix
            return matrix
        except Exception as e:
            import warnings
            warnings.warn(f"OSRM table failed ({type(e).__name__}: {e}), falling back to Haversine.")
            return self._fallback.compute_matrix(locations)
