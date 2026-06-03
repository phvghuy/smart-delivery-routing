from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
from uuid import UUID

from ..shared.value_objects import Capacity


class DriverStatus(IntEnum):
    AVAILABLE = 1
    DELIVERING = 2
    OFFLINE = 3
    INACTIVE = 0


@dataclass(frozen=True)
class DriverProfile:
    name: str
    phone: str
    plate_number: str


@dataclass
class Driver:
    id: UUID
    profile: DriverProfile
    current_hub_id: UUID
    capacity: Capacity
    status: DriverStatus
    fcm_token: str
    deleted_at: datetime | None = None
    hub_name: str = ""  # populated from DB join, not a domain concern


class DeliveryRouteStatus(IntEnum):
    PLANNED = 1
    IN_PROGRESS = 2
    COMPLETED = 3
    CANCELLED = 4


@dataclass
class DeliveryRoute:
    id: UUID
    driver_id: UUID
    hub_id: UUID
    status: DeliveryRouteStatus
    total_distance_km: float
    created_at: datetime


class RouteStopStatus(IntEnum):
    PENDING = 1
    DELIVERED = 2
    FAILED = 3


class FailedReason(IntEnum):
    CUSTOMER_ABSENT = 1
    WRONG_ADDRESS = 2
    CUSTOMER_REJECTED = 3
    CANNOT_CONTACT = 4
    OTHER = 5


@dataclass
class RouteStop:
    id: UUID
    route_id: UUID
    parcel_id: UUID
    status: RouteStopStatus
    sequence: int
    failed_reason: FailedReason | None = None
    completed_at: datetime | None = None
