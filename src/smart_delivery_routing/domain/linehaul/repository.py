from abc import ABC, abstractmethod
from uuid import UUID

from .models import Hub, Parcel, ParcelStatus, Truck, TruckTrip, TruckTripItem
from .queries import HubQuery, ParcelQuery, TruckQuery


class ParcelRepository(ABC):
    @abstractmethod
    def get_by_id(self, parcel_id: UUID) -> Parcel | None: ...

    @abstractmethod
    def list(self, query: ParcelQuery) -> list[Parcel]: ...


class HubRepository(ABC):
    @abstractmethod
    def create(self, hub: Hub) -> Hub: ...

    @abstractmethod
    def get_by_id(self, hub_id: UUID) -> Hub | None: ...

    @abstractmethod
    def list(self, query: HubQuery) -> tuple[list[Hub], int]: ...

    @abstractmethod
    def update(self, hub: Hub) -> Hub: ...

    @abstractmethod
    def delete(self, hub_id: UUID) -> None: ...


class TruckRepository(ABC):
    @abstractmethod
    def create(self, truck: Truck) -> Truck: ...

    @abstractmethod
    def get_by_id(self, truck_id: UUID) -> Truck | None: ...

    @abstractmethod
    def list(self, query: TruckQuery) -> tuple[list[Truck], int]: ...

    @abstractmethod
    def update(self, truck: Truck) -> Truck: ...

    @abstractmethod
    def delete(self, truck_id: UUID) -> None: ...

