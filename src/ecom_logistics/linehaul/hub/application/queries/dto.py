from dataclasses import dataclass
from ecom_logistics.linehaul.hub.domain import Hub, HubStatus, HubType


@dataclass(frozen=True)
class HubQuery:
    page: int = 1
    page_size: int = 20
    search: str | None = None
    statuses: list[HubStatus] | None = None
    types: list[HubType] | None = None
    include_deleted: bool = False


@dataclass(frozen=True)
class PagedHubs:
    items: list[Hub]
    total: int
    page: int
    size: int

    @property
    def pages(self) -> int:
        return max(1, -(-self.total // self.size))
    