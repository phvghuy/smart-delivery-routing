from uuid import UUID
from ecom_logistics.linehaul.hub.domain import HubRepository
from ecom_logistics.linehaul.hub.application.exceptions import HubNotFound


class DeleteHubUseCase:
    def __init__(self, repo: HubRepository):
        self._repo = repo

    def execute(self, hub_id: UUID) -> None:
        if self._repo.get_by_id(hub_id) is None:
            raise HubNotFound(hub_id=hub_id)
        return self._repo.delete(hub_id)