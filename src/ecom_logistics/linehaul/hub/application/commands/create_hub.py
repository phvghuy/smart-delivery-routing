from uuid import uuid4
from ecom_logistics.shared import Address, Location
from ecom_logistics.linehaul.hub.domain import Hub, HubType, HubRepository, HubStatus


class CreateHubUseCase:
    def __init__(self, repo: HubRepository):
        self._repo = repo

    def execute(
            self, 
            name: str,
            type: HubType,
            address_text: str,
            lat: float,
            lng: float,
        ) -> Hub:
        hub = Hub(
            id=uuid4(),
            name=name,
            type=type,
            address=Address(
                text=address_text,
                location=Location(lat=lat, lng=lng),
            ),
            status=HubStatus.ACTIVE
        )
        return self._repo.create(hub)
