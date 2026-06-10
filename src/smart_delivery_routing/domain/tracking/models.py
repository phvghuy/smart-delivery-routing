from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
from uuid import UUID

from ..linehaul import ParcelStatus


class TrackingLocationType(IntEnum):
    SYSTEM = 1
    HUB = 2
    DRIVER = 3
    CUSTOMER = 4
    TRUCK_TRIP = 5


@dataclass(frozen=True)
class TrackingLocation:
    kind: TrackingLocationType
    name: str
    id: UUID | None = None


@dataclass(frozen=True)
class TrackingEvent:
    id: UUID
    parcel_id: UUID
    status: ParcelStatus
    location: TrackingLocation
    created_at: datetime
    note: str | None = None
