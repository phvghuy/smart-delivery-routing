import numpy as np

from smart_delivery_routing.domain.models import Location
from smart_delivery_routing.domain.ports import DistanceCalculator

_EARTH_RADIUS_KM = 6371.0


def _haversine_matrix(lats: np.ndarray, lngs: np.ndarray) -> np.ndarray:
    lats = np.radians(lats)
    lngs = np.radians(lngs)
    dlat = lats[:, None] - lats[None, :]
    dlng = lngs[:, None] - lngs[None, :]
    h = np.sin(dlat / 2) ** 2 + np.cos(lats[:, None]) * np.cos(lats[None, :]) * np.sin(dlng / 2) ** 2
    return 2 * _EARTH_RADIUS_KM * np.arcsin(np.sqrt(h))


class HaversineDistanceCalculator(DistanceCalculator):
    def compute_matrix(self, locations: list[Location]) -> list[list[float]]:
        lats = np.array([loc.lat for loc in locations])
        lngs = np.array([loc.lng for loc in locations])
        return _haversine_matrix(lats, lngs).tolist()
