from dataclasses import dataclass
from uuid import UUID
from ecom_logistics.shared.exceptions import NotFoundError


@dataclass(frozen=True)
class HubNotFound(NotFoundError):
    hub_id: UUID

    def __str__(self) -> str:
        return f"Hub '{self.hub_id}' not found."