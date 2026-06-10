from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from .models import HubStatus, HubType, ParcelStatus, TruckStatus, TruckTripStatus


@dataclass(frozen=True)
class HubQuery:
    page: int = 1
    page_size: int = 20
    search: str | None = None
    statuses: list[HubStatus] | None = None
    types: list[HubType] | None = None
    include_deleted: bool = False


@dataclass(frozen=True)
class ParcelQuery:
    page_size: int = 20
    statuses: list[ParcelStatus] | None = None
    cursor_created_at: datetime | None = None
    cursor_id: UUID | None = None


@dataclass(frozen=True)
class TruckQuery:
    page: int = 1
    page_size: int = 20
    search: str | None = None
    statuses: list[TruckStatus] | None = None
    include_deleted: bool = False


@dataclass(frozen=True)
class TruckTripQuery:
    page: int = 1
    page_size: int = 20
    statuses: list[TruckTripStatus] | None = None
    include_deleted: bool = False
