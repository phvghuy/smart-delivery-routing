from dataclasses import dataclass

from .models import HubStatus, HubType, Truck, TruckStatus


@dataclass(frozen=True)
class HubQuery:
    page: int = 1
    page_size: int = 20
    search: str | None = None
    statuses: list[HubStatus] | None = None
    types: list[HubType] | None = None
    include_deleted: bool = False


@dataclass(frozen=True)
class TruckQuery:
    page: int = 1
    page_size: int = 20
    search: str | None = None
    statuses: list[TruckStatus] | None = None
    include_deleted: bool = False
