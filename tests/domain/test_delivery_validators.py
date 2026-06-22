from datetime import datetime, timezone
from uuid import uuid4

from smart_delivery_routing.domain.delivery import Driver, DriverStatus, DeliveryRoute, DeliveryRouteStatus, RouteStop, RouteStopStatus
from smart_delivery_routing.domain.delivery.models import DriverProfile, FailedReason
from smart_delivery_routing.domain.delivery.validators import validate_driver, validate_delivery_route, validate_route_stop
from smart_delivery_routing.domain.shared import Capacity, Location


def _make_driver(**overrides) -> Driver:
    defaults = dict(
        id=uuid4(),
        profile=DriverProfile(name="Nguyen Van A", phone="0901234567", plate_number="51A-12345"),
        current_hub_id=uuid4(),
        capacity=Capacity(max_weight=100.0, max_volume=1.0),
        status=DriverStatus.AVAILABLE,
        fcm_token="token-abc",
    )
    return Driver(**{**defaults, **overrides})


def _make_route(**overrides) -> DeliveryRoute:
    defaults = dict(
        id=uuid4(),
        driver_id=uuid4(),
        hub_id=uuid4(),
        status=DeliveryRouteStatus.PLANNED,
        total_distance_km=10.5,
        created_at=datetime.now(timezone.utc),
    )
    return DeliveryRoute(**{**defaults, **overrides})


def _make_stop(**overrides) -> RouteStop:
    defaults = dict(
        id=uuid4(),
        route_id=uuid4(),
        parcel_id=uuid4(),
        status=RouteStopStatus.PENDING,
        sequence=1,
        location=Location(lat=10.78, lng=106.70),
        failed_reason=None,
        completed_at=None,
    )
    return RouteStop(**{**defaults, **overrides})


# ── validate_driver ───────────────────────────────────────────────────────────

def test_validate_driver_valid():
    assert validate_driver(_make_driver()) == []

def test_validate_driver_empty_name():
    driver = _make_driver(profile=DriverProfile(name="", phone="0901234567", plate_number="51A-12345"))
    errors = validate_driver(driver)
    assert any(e.field == "profile.name" for e in errors)

def test_validate_driver_invalid_phone():
    driver = _make_driver(profile=DriverProfile(name="A", phone="12345", plate_number="51A-12345"))
    errors = validate_driver(driver)
    assert any(e.field == "profile.phone" for e in errors)

def test_validate_driver_empty_plate():
    driver = _make_driver(profile=DriverProfile(name="A", phone="0901234567", plate_number=""))
    errors = validate_driver(driver)
    assert any(e.field == "profile.plate_number" for e in errors)

def test_validate_driver_zero_weight_capacity():
    errors = validate_driver(_make_driver(capacity=Capacity(max_weight=0.0, max_volume=1.0)))
    assert any(e.field == "capacity.max_weight" for e in errors)

def test_validate_driver_zero_volume_capacity():
    errors = validate_driver(_make_driver(capacity=Capacity(max_weight=100.0, max_volume=0.0)))
    assert any(e.field == "capacity.max_volume" for e in errors)


# ── validate_delivery_route ───────────────────────────────────────────────────

def test_validate_delivery_route_valid():
    assert validate_delivery_route(_make_route()) == []

def test_validate_delivery_route_zero_distance_is_valid():
    assert validate_delivery_route(_make_route(total_distance_km=0.0)) == []

def test_validate_delivery_route_negative_distance():
    errors = validate_delivery_route(_make_route(total_distance_km=-1.0))
    assert any(e.field == "total_distance_km" for e in errors)


# ── validate_route_stop ───────────────────────────────────────────────────────

def test_validate_route_stop_valid():
    assert validate_route_stop(_make_stop()) == []

def test_validate_route_stop_sequence_zero():
    errors = validate_route_stop(_make_stop(sequence=0))
    assert any(e.field == "sequence" for e in errors)

def test_validate_route_stop_sequence_negative():
    errors = validate_route_stop(_make_stop(sequence=-1))
    assert any(e.field == "sequence" for e in errors)

def test_validate_route_stop_failed_reason_without_failed_status():
    stop = _make_stop(status=RouteStopStatus.PENDING, failed_reason=FailedReason.CUSTOMER_ABSENT)
    errors = validate_route_stop(stop)
    assert any(e.field == "failed_reason" for e in errors)

def test_validate_route_stop_completed_at_without_delivered_status():
    stop = _make_stop(status=RouteStopStatus.PENDING, completed_at=datetime.now(timezone.utc))
    errors = validate_route_stop(stop)
    assert any(e.field == "completed_at" for e in errors)

def test_validate_route_stop_failed_reason_with_failed_status_is_valid():
    stop = _make_stop(status=RouteStopStatus.FAILED, failed_reason=FailedReason.WRONG_ADDRESS)
    assert validate_route_stop(stop) == []

def test_validate_route_stop_completed_at_with_delivered_status_is_valid():
    stop = _make_stop(status=RouteStopStatus.DELIVERED, completed_at=datetime.now(timezone.utc))
    assert validate_route_stop(stop) == []
