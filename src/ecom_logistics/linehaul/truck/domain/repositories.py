from abc import ABC, abstractmethod
from uuid import UUID
from .entities import Truck


class TruckRepository(ABC):
    @abstractmethod
    def get_by_id(self, truck_id: UUID) -> Truck | None: ...
    
    @abstractmethod
    def create(self, truck: Truck) -> Truck: ...

    @abstractmethod
    def update(self, truck: Truck) -> Truck: ...

    @abstractmethod
    def delete(self, truck_id: UUID) -> None: ...
