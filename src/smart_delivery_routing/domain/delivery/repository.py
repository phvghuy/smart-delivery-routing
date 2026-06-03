from abc import ABC, abstractmethod
from uuid import UUID

from .models import DeliveryRoute, Driver, DriverStatus, RouteStop
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

