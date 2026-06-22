from datetime import datetime, timezone
from uuid import uuid4

from smart_delivery_routing.domain.linehaul import (
    Hub, HubStatus, HubType,
    Parcel, ParcelStatus,
    Truck, TruckStatus,
    TruckTrip, TruckTripStatus,
    TruckTripItem,
)
from smart_delivery_routing.domain.linehaul.validators import (
    validate_hub,
    validate_parcel,
    validate_truck,
    validate_truck_trip,
    validate_truck_trip_item,
)
from smart_delivery_routing.domain.shared import Address, Capacity, Load, Location


def _make_hub(**overrides) -> Hub:
    defaults = dict(
        id=uuid4(),
        name="Hub A",
        type=HubType.SORTING_CENTER,
        address=Address(text="123 Nguyen Hue", location=Location(lat=10.78, lng=106.70)),
        status=HubStatus.ACTIVE,
    )
    return Hub(**{**defaults, **overrides})


def _make_parcel(**overrides) -> Parcel:
    now = datetime.now(timezone.utc)
    defaults = dict(
        id=uuid4(),
        shipping_request_id=uuid4(),
        tracking_number="TRK-001",
        origin_hub_id=uuid4(),
        destination_hub_id=uuid4(),
        load=Load(weight=5.0, volume=0.1),
        created_at=now,
        updated_at=now,
    )
    return Parcel(**{**defaults, **overrides})


def _make_truck(**overrides) -> Truck:
    defaults = dict(
        id=uuid4(),
        plate_number="51A-12345",
        capacity=Capacity(max_weight=1000.0, max_volume=10.0),
        status=TruckStatus.AVAILABLE,
    )
    return Truck(**{**defaults, **overrides})


def _make_truck_trip(**overrides) -> TruckTrip:
    now = datetime.now(timezone.utc)
    defaults = dict(
        id=uuid4(),
        truck_id=uuid4(),
        origin_hub_id=uuid4(),
        destination_hub_id=uuid4(),
        status=TruckTripStatus.PLANNED,
        planned_departure_time=now,
        created_at=now,
    )
    return TruckTrip(**{**defaults, **overrides})


def _make_truck_trip_item(**overrides) -> TruckTripItem:
    now = datetime.now(timezone.utc)
    defaults = dict(
        id=uuid4(),
        truck_trip_id=uuid4(),
        parcel_id=uuid4(),
        loaded_at=now,
    )
    return TruckTripItem(**{**defaults, **overrides})


# ── validate_hub ──────────────────────────────────────────────────────────────

def test_validate_hub_valid():
    assert validate_hub(_make_hub()) == []

def test_validate_hub_empty_name():
    errors = validate_hub(_make_hub(name=""))
    assert any(e.field == "name" for e in errors)

def test_validate_hub_empty_address_text():
    bad_address = Address(text="", location=Location(lat=10.78, lng=106.70))
    errors = validate_hub(_make_hub(address=bad_address))
    assert any(e.field == "address.text" for e in errors)

def test_validate_hub_invalid_lat():
    bad_address = Address(text="abc", location=Location(lat=999.0, lng=106.70))
    errors = validate_hub(_make_hub(address=bad_address))
    assert any(e.field == "address.lat" for e in errors)

def test_validate_hub_invalid_lng():
    bad_address = Address(text="abc", location=Location(lat=10.78, lng=999.0))
    errors = validate_hub(_make_hub(address=bad_address))
    assert any(e.field == "address.lng" for e in errors)


# ── validate_parcel ───────────────────────────────────────────────────────────

def test_validate_parcel_valid():
    assert validate_parcel(_make_parcel()) == []

def test_validate_parcel_empty_tracking_number():
    errors = validate_parcel(_make_parcel(tracking_number=""))
    assert any(e.field == "tracking_number" for e in errors)

def test_validate_parcel_same_origin_and_destination():
    hub_id = uuid4()
    errors = validate_parcel(_make_parcel(origin_hub_id=hub_id, destination_hub_id=hub_id))
    assert len(errors) > 0

def test_validate_parcel_zero_weight():
    errors = validate_parcel(_make_parcel(load=Load(weight=0.0, volume=0.1)))
    assert any(e.field == "load.weight" for e in errors)

def test_validate_parcel_zero_volume():
    errors = validate_parcel(_make_parcel(load=Load(weight=5.0, volume=0.0)))
    assert any(e.field == "load.volume" for e in errors)


# ── validate_truck ────────────────────────────────────────────────────────────

def test_validate_truck_valid():
    assert validate_truck(_make_truck()) == []

def test_validate_truck_empty_plate():
    errors = validate_truck(_make_truck(plate_number=""))
    assert any(e.field == "plate_number" for e in errors)

def test_validate_truck_zero_max_weight():
    errors = validate_truck(_make_truck(capacity=Capacity(max_weight=0.0, max_volume=10.0)))
    assert any(e.field == "capacity.max_weight" for e in errors)

def test_validate_truck_zero_max_volume():
    errors = validate_truck(_make_truck(capacity=Capacity(max_weight=1000.0, max_volume=0.0)))
    assert any(e.field == "capacity.max_volume" for e in errors)


# ── validate_truck_trip ───────────────────────────────────────────────────────

def test_validate_truck_trip_valid():
    assert validate_truck_trip(_make_truck_trip()) == []

def test_validate_truck_trip_same_hubs():
    hub_id = uuid4()
    errors = validate_truck_trip(_make_truck_trip(origin_hub_id=hub_id, destination_hub_id=hub_id))
    assert len(errors) > 0

def test_validate_truck_trip_departure_before_planned():
    from datetime import timedelta
    now = datetime.now(timezone.utc)
    trip = _make_truck_trip(
        planned_departure_time=now,
        actual_departure_time=now - timedelta(hours=1),
    )
    errors = validate_truck_trip(trip)
    assert any(e.field == "actual_departure_time" for e in errors)

def test_validate_truck_trip_arrival_before_departure():
    from datetime import timedelta
    now = datetime.now(timezone.utc)
    trip = _make_truck_trip(
        planned_departure_time=now,
        actual_departure_time=now,
        actual_arrival_time=now - timedelta(hours=1),
    )
    errors = validate_truck_trip(trip)
    assert any(e.field == "actual_arrival_time" for e in errors)


# ── validate_truck_trip_item ──────────────────────────────────────────────────

def test_validate_truck_trip_item_valid():
    assert validate_truck_trip_item(_make_truck_trip_item()) == []

def test_validate_truck_trip_item_no_unload_is_valid():
    assert validate_truck_trip_item(_make_truck_trip_item(unloaded_at=None)) == []

def test_validate_truck_trip_item_unloaded_before_loaded():
    from datetime import timedelta
    now = datetime.now(timezone.utc)
    item = _make_truck_trip_item(
        loaded_at=now,
        unloaded_at=now - timedelta(minutes=10),
    )
    errors = validate_truck_trip_item(item)
    assert any(e.field == "unloaded_at" for e in errors)
