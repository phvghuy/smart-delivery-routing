from abc import ABC, abstractmethod

from .models import Location, Order, RoutingResult, Vehicle


class DistanceCalculator(ABC):
    @abstractmethod
    def compute_matrix(self, locations: list[Location]) -> list[list[float]]:
        """Return an N×N matrix where matrix[i][j] is distance in km from location i to j."""


class RouteSolver(ABC):
    @abstractmethod
    def solve(
        self,
        orders: list[Order],
        vehicles: list[Vehicle],
        distance_matrix: list[list[float]],
    ) -> RoutingResult:
        """Assign orders to vehicles and return optimized routes."""