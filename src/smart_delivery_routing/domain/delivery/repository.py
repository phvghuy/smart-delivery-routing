from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from .models import DeliveryRoute, DeliveryRouteStatus, Driver, RouteStop
from .queries import DriverQuery


class DriverRepository(ABC):
    @abstractmethod
    def create(self, driver: Driver) -> Driver: ...

    @abstractmethod
    def get_by_id(self, driver_id: UUID) -> Driver | None: ...

    @abstractmethod
    def list(self, query: DriverQuery) -> tuple[list[Driver], int]: ...

    @abstractmethod
    def update(self, driver: Driver) -> Driver: ...

    @abstractmethod
    def delete(self, driver_id: UUID) -> None: ...

    @abstractmethod
    def update_fcm_token(self, driver_id: str, fcm_token: str) -> None: ...

    @abstractmethod
    def list_available(self) -> list[Driver]: ...


class DeliveryRouteRepository(ABC):
    @abstractmethod
    def save(self, route: DeliveryRoute) -> DeliveryRoute: ...

    @abstractmethod
    def get_by_id(self, route_id: UUID) -> DeliveryRoute | None: ...

    @abstractmethod
    def get_by_driver_id(self, driver_id: UUID) -> DeliveryRoute | None: ...

    @abstractmethod
    def list_all(self, date: str | None = None, status: DeliveryRouteStatus | None = None) -> list[DeliveryRoute]: ...

    @abstractmethod
    def update(self, route: DeliveryRoute) -> DeliveryRoute: ...


class RouteStopRepository(ABC):
    @abstractmethod
    def save(self, stop: RouteStop) -> RouteStop: ...

    @abstractmethod
    def list_active_parcel_ids(self) -> list[UUID]: ...

    @abstractmethod
    def list_by_route_id(self, route_id: UUID) -> list[RouteStop]: ...

    @abstractmethod
    def update(self, stop: RouteStop) -> RouteStop: ...
