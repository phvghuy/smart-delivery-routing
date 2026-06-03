from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
from uuid import UUID

from ..shared.value_objects import Address, Capacity, Load


class ParcelStatus(IntEnum):
    AWAITING_PICKUP = 1
    PICKED_UP = 2
    AT_ORIGIN_HUB = 3
    IN_LINEHAUL_TRANSIT = 4
    AT_DESTINATION_HUB = 5
    OUT_FOR_DELIVERY = 6
    DELIVERED = 7
    DELIVERY_FAILED = 8
    RETURNED = 9
    CANCELLED = 10


@dataclass
class Parcel:
    id: UUID
    shipping_request_id: UUID
    tracking_number: str
    origin_hub_id: UUID
    destination_hub_id: UUID
    load: Load
    created_at: datetime
    updated_at: datetime
    current_hub_id: UUID | None = None
    status: ParcelStatus = ParcelStatus.AWAITING_PICKUP


class HubType(IntEnum):
    SORTING_CENTER = 1
    LOCAL_HUB = 2


class HubStatus(IntEnum):
    ACTIVE = 1
    INACTIVE = 0


@dataclass
class Hub:
    id: UUID
    name: str
    type: HubType
    address: Address
    status: HubStatus = HubStatus.ACTIVE
    deleted_at: datetime | None = None


class TruckStatus(IntEnum):
    AVAILABLE = 1
    IN_TRANSIT = 2
    INACTIVE = 0


@dataclass
class Truck:
    id: UUID
    plate_number: str
    capacity: Capacity
    status: TruckStatus = TruckStatus.AVAILABLE
    deleted_at: datetime | None = None


class TruckTripStatus(IntEnum):
    PLANNED = 1
    DEPARTED = 2
    ARRIVED = 3
    CANCELLED = 4


@dataclass
class TruckTrip:
    id: UUID
    truck_id: UUID
    origin_hub_id: UUID
    destination_hub_id: UUID
    status: TruckTripStatus
    planned_departure_time: datetime
    created_at: datetime
    actual_departure_time: datetime | None = None
    actual_arrival_time: datetime | None = None


@dataclass
class TruckTripItem:
    id: UUID
    truck_trip_id: UUID
    parcel_id: UUID
    loaded_at: datetime
    unloaded_at: datetime | None = None
