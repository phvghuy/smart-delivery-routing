import pytest

from smart_delivery_routing.domain.models import Location, Order, Vehicle
from smart_delivery_routing.domain.validators import (
    _check_lat,
    _check_lng,
    _check_order_duplicate_id,
    _check_order_volume_fits_vehicle,
    _check_order_volume_positive,
    _check_order_weight_fits_vehicle,
    _check_order_weight_positive,
    _check_vehicle_duplicate_id,
    _check_vehicle_max_volume_positive,
    _check_vehicle_max_weight_positive,
    validate_orders,
    validate_vehicles,
)
from tests.conftest import make_order, make_vehicle


# --- _check_lat ---

def test_check_lat_valid():
    assert _check_lat("X", "lat", 10.78) is None

def test_check_lat_above_90():
    error = _check_lat("X", "lat", 91.0)
    assert error is not None
    assert error.field == "lat"

def test_check_lat_below_minus90():
    assert _check_lat("X", "lat", -91.0) is not None

def test_check_lat_boundary():
    assert _check_lat("X", "lat", 90.0) is None
    assert _check_lat("X", "lat", -90.0) is None


# --- _check_lng ---

def test_check_lng_valid():
    assert _check_lng("X", "lng", 106.70) is None

def test_check_lng_out_of_range():
    assert _check_lng("X", "lng", 181.0) is not None
    assert _check_lng("X", "lng", -181.0) is not None

def test_check_lng_boundary():
    assert _check_lng("X", "lng", 180.0) is None
    assert _check_lng("X", "lng", -180.0) is None


# --- _check_order_weight_positive / volume_positive ---

def test_weight_positive_valid():
    assert _check_order_weight_positive(make_order(weight=1.0)) is None

def test_weight_zero_invalid():
    assert _check_order_weight_positive(make_order(weight=0.0)) is not None

def test_weight_negative_invalid():
    assert _check_order_weight_positive(make_order(weight=-5.0)) is not None

def test_volume_positive_valid():
    assert _check_order_volume_positive(make_order(volume=0.1)) is None

def test_volume_zero_invalid():
    assert _check_order_volume_positive(make_order(volume=0.0)) is not None


# --- _check_order_weight_fits_vehicle / volume_fits_vehicle ---

def test_weight_fits_vehicle():
    assert _check_order_weight_fits_vehicle(make_order(weight=100.0), max_vehicle_weight=500.0) is None

def test_weight_exceeds_vehicle():
    error = _check_order_weight_fits_vehicle(make_order(weight=600.0), max_vehicle_weight=500.0)
    assert error is not None
    assert "500.0" in error.reason

def test_volume_fits_vehicle():
    assert _check_order_volume_fits_vehicle(make_order(volume=0.5), max_vehicle_volume=2.0) is None

def test_volume_exceeds_vehicle():
    assert _check_order_volume_fits_vehicle(make_order(volume=3.0), max_vehicle_volume=2.0) is not None


# --- duplicate ID ---

def test_order_duplicate_id_first_occurrence():
    seen: set[str] = set()
    assert _check_order_duplicate_id(make_order("ORD-001"), seen) is None

def test_order_duplicate_id_second_occurrence():
    seen = {"ORD-001"}
    error = _check_order_duplicate_id(make_order("ORD-001"), seen)
    assert error is not None
    assert error.entity_id == "ORD-001"

def test_vehicle_duplicate_id():
    seen = {"VEH-001"}
    assert _check_vehicle_duplicate_id(make_vehicle("VEH-001"), seen) is not None


# --- vehicle max_weight / max_volume ---

def test_vehicle_max_weight_positive():
    assert _check_vehicle_max_weight_positive(make_vehicle(max_weight=500.0)) is None
    assert _check_vehicle_max_weight_positive(make_vehicle(max_weight=0.0)) is not None

def test_vehicle_max_volume_positive():
    assert _check_vehicle_max_volume_positive(make_vehicle(max_volume=2.0)) is None
    assert _check_vehicle_max_volume_positive(make_vehicle(max_volume=-1.0)) is not None


# --- validate_orders (integration) ---

def test_validate_orders_no_errors(small_orders, small_vehicles):
    assert validate_orders(small_orders, small_vehicles) == []

def test_validate_orders_duplicate_id(small_vehicles):
    orders = [make_order("ORD-001"), make_order("ORD-001")]
    errors = validate_orders(orders, small_vehicles)
    assert any(e.field == "order_id" for e in errors)

def test_validate_orders_over_capacity(small_vehicles):
    heavy = make_order(weight=9999.0)
    errors = validate_orders([heavy], small_vehicles)
    assert any(e.field == "weight" for e in errors)

def test_validate_orders_multiple_errors(small_vehicles):
    bad = make_order(lat=999.0, weight=-1.0)
    errors = validate_orders([bad], small_vehicles)
    fields = {e.field for e in errors}
    assert "lat" in fields
    assert "weight" in fields


# --- validate_vehicles (integration) ---

def test_validate_vehicles_no_errors(small_vehicles):
    assert validate_vehicles(small_vehicles) == []

def test_validate_vehicles_invalid_depot():
    vehicle = Vehicle(
        vehicle_id="VEH-BAD",
        depot=Location(lat=999.0, lng=106.65),
        max_weight=500.0,
        max_volume=2.0,
    )
    errors = validate_vehicles([vehicle])
    assert any(e.field == "depot.lat" for e in errors)