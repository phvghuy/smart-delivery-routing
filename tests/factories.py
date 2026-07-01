from datetime import datetime, timezone
from uuid import uuid4

from smart_delivery_routing.domain.linehaul.models import (
    Parcel, ParcelStatus, Truck, TruckStatus, TruckTrip, TruckTripStatus,
)
from smart_delivery_routing.domain.shared import Capacity, Load


def make_parcel(**overrides) -> Parcel:
    defaults = dict(
        id=uuid4(),
        shipping_request_id=uuid4(),
        tracking_number=str(uuid4()),
        origin_hub_id=uuid4(),
        destination_hub_id=uuid4(),
        load=Load(weight=1.0, volume=1.0),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        current_hub_id=None,
        status=ParcelStatus.AWAITING_PICKUP,
        origin_hub_name="Hub A",
        destination_hub_name="Hub B",
        current_hub_name="",
    )
    return Parcel(**{**defaults, **overrides})


def make_truck(**overrides) -> Truck:
    defaults = dict(
        id=uuid4(),
        plate_number="51A-123.45",
        capacity=Capacity(max_weight=1000.0, max_volume=10.0),
        status=TruckStatus.AVAILABLE,
    )
    return Truck(**{**defaults, **overrides})


def make_truck_trip(**overrides) -> TruckTrip:
    defaults = dict(
        id=uuid4(),
        truck_id=uuid4(),
        origin_hub_id=uuid4(),
        destination_hub_id=uuid4(),
        status=TruckTripStatus.PLANNED,
        planned_departure_time=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
        truck_plate_number="51A-123.45",
        origin_hub_name="Hub A",
        destination_hub_name="Hub B",
    )
    return TruckTrip(**{**defaults, **overrides})