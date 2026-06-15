from abc import ABC, abstractmethod
from .entities import Hub
from uuid import UUID

class HubRepository(ABC):
    @abstractmethod
    def get_by_id(self, hub_id: UUID) -> Hub | None: ...

    @abstractmethod
    def create(self, hub: Hub) -> Hub: ...

    @abstractmethod
    def update(self, hub: Hub) -> Hub: ...

    @abstractmethod
    def delete(self, hub_id: UUID) -> None: ...
