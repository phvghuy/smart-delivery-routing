from abc import ABC, abstractmethod
from uuid import UUID

from .models import TrackingEvent

class TrackingEventRepository(ABC):
    @abstractmethod
    def create(self, event: TrackingEvent) -> TrackingEvent: ...

    @abstractmethod
    def list_by_parcel_id(self, parcel_id: UUID) -> list[TrackingEvent]: ...
