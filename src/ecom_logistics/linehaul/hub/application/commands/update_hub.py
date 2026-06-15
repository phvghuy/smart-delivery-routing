from uuid import UUID
from ecom_logistics.shared import Address, Location
from ecom_logistics.linehaul.hub.application.exceptions import HubNotFound
from ecom_logistics.linehaul.hub.domain import Hub, HubType, HubRepository, HubStatus


class UpdateHubUseCase:
    def __init__(self, repo: HubRepository):
        self._repo = repo

    def execute(
            self, 
            id: UUID,
            name: str,
            type: HubType,
            address_text: str,
            lat: float,
            lng: float,
            status: HubStatus,
        ) -> Hub:
        hub = Hub(
            id=id,
            name=name,
            type=type,
            address=Address(
                text=address_text,
                location=Location(lat=lat, lng=lng),
            ),
            status=status,
        )
        if self._repo.get_by_id(hub.id) is None:
            raise HubNotFound(hub_id=hub.id)
        return self._repo.update(hub)
