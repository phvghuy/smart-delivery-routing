from abc import ABC, abstractmethod
from dataclasses import dataclass

from smart_delivery_routing.domain.models import Location, Order, RoutingResult, Vehicle, Warehouse


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
        warehouses: list[Warehouse],
        distance_matrix: list[list[float]],
    ) -> RoutingResult:
        """Assign orders to vehicles and return optimized routes."""


@dataclass(frozen=True)
class AuthToken:
    access_token: str
    role: str


class AuthService(ABC):
    @abstractmethod
    def sign_in(self, email: str, password: str) -> AuthToken: ...

    @abstractmethod
    def sign_out(self, token: str) -> None: ...


class JobNotFound(Exception):
    pass


@dataclass(frozen=True)
class JobStatus:
    job_id: str
    status: str
    result: dict | None = None
    error: str | None = None


class JobService(ABC):
    @abstractmethod
    def submit(self, token: str) -> str: ...

    @abstractmethod
    def get_status(self, job_id: str) -> JobStatus: ...


class NotificationService(ABC):
    @abstractmethod
    def send_route_notification(
        self,
        driver_id: str,
        fcm_token: str,
        vehicle_id: str,
        stops_count: int,
        distance_km: float,
        job_id: str,
    ) -> None: ...
