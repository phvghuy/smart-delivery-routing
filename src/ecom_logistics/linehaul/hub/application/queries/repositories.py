from abc import ABC, abstractmethod
from uuid import UUID
from ecom_logistics.linehaul.hub.domain import Hub
from .dto import HubQuery


class HubQueryRepository(ABC):
    @abstractmethod
    def get_by_id(self, hub_id: UUID) -> Hub | None: ...

    @abstractmethod
    def list(self, query: HubQuery) -> tuple[list[Hub], int]: ...
