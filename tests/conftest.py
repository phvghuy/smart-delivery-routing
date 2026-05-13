import pytest

from smart_delivery_routing.domain.models import Location, Order, Vehicle, Warehouse

WH_ID = "WH-001"
WAREHOUSE_LOC = Location(lat=10.98, lng=106.65)


def make_warehouse(warehouse_id: str = WH_ID) -> Warehouse:
    return Warehouse(warehouse_id=warehouse_id, location=WAREHOUSE_LOC)


def make_order(
    order_id: str = "ORD-001",
    lat: float = 10.78,
    lng: float = 106.70,
    weight: float = 50.0,
    volume: float = 0.5,
    warehouse_id: str = WH_ID,
) -> Order:
    return Order(
        order_id=order_id,
        warehouse_id=warehouse_id,
        location=Location(lat=lat, lng=lng),
        weight=weight,
        volume=volume,
    )


def make_vehicle(
    vehicle_id: str = "VEH-001",
    max_weight: float = 500.0,
    max_volume: float = 2.0,
    warehouse_id: str = WH_ID,
) -> Vehicle:
    return Vehicle(
        vehicle_id=vehicle_id,
        current_warehouse_id=warehouse_id,
        max_weight=max_weight,
        max_volume=max_volume,
    )


@pytest.fixture
def warehouse():
    return make_warehouse()


@pytest.fixture
def small_warehouses():
    return [make_warehouse()]


@pytest.fixture
def one_order():
    return make_order()


@pytest.fixture
def one_vehicle():
    return make_vehicle()


@pytest.fixture
def small_orders():
    return [
        make_order("ORD-001", lat=10.78, lng=106.70, weight=50.0, volume=0.3),
        make_order("ORD-002", lat=10.80, lng=106.72, weight=80.0, volume=0.4),
        make_order("ORD-003", lat=10.76, lng=106.68, weight=30.0, volume=0.2),
    ]


@pytest.fixture
def small_vehicles():
    return [
        make_vehicle("VEH-001", max_weight=200.0, max_volume=1.0),
        make_vehicle("VEH-002", max_weight=200.0, max_volume=1.0),
    ]
