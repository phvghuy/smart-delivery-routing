from .repositories import HubQueryRepository
from uuid import UUID
from ecom_logistics.linehaul.hub.domain import Hub
from ecom_logistics.linehaul.hub.application.exceptions import HubNotFound


class GetHubUseCase:
    def __init__(self, repo: HubQueryRepository):
        self._repo = repo

    def execute(self, hub_id: UUID) -> Hub:
        hub = self._repo.get_by_id(hub_id)
        if hub is None:
            raise HubNotFound(hub_id=hub_id)
        return hub
