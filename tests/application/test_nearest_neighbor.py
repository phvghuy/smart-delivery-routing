import pytest

from smart_delivery_routing.application.solvers.nearest_neighbor import NearestNeighborSolver
from smart_delivery_routing.infrastructure.distance import HaversineDistanceCalculator
from tests.conftest import make_order, make_vehicle, DEPOT

solver = NearestNeighborSolver()
calculator = HaversineDistanceCalculator()


def _matrix(orders, vehicles):
    locations = [vehicles[0].depot] + [o.location for o in orders]
    return calculator.compute_matrix(locations)


# --- basic assignment ---

def test_all_orders_assigned_when_capacity_sufficient(small_orders, small_vehicles):
    matrix = _matrix(small_orders, small_vehicles)
    result = solver.solve(small_orders, small_vehicles, matrix)
    assigned = {s.order_id for r in result.routes for s in r.stops}
    assert assigned == {o.order_id for o in small_orders}
    assert result.unassigned_orders == []


def test_vehicles_used_does_not_exceed_available(small_orders, small_vehicles):
    matrix = _matrix(small_orders, small_vehicles)
    result = solver.solve(small_orders, small_vehicles, matrix)
    assert result.vehicles_used <= len(small_vehicles)


def test_total_distance_positive(small_orders, small_vehicles):
    matrix = _matrix(small_orders, small_vehicles)
    result = solver.solve(small_orders, small_vehicles, matrix)
    assert result.total_distance > 0


def test_total_distance_equals_sum_of_routes(small_orders, small_vehicles):
    matrix = _matrix(small_orders, small_vehicles)
    result = solver.solve(small_orders, small_vehicles, matrix)
    assert result.total_distance == pytest.approx(sum(r.total_distance for r in result.routes))


# --- capacity constraints ---

def test_no_route_exceeds_weight_capacity(small_orders, small_vehicles):
    matrix = _matrix(small_orders, small_vehicles)
    result = solver.solve(small_orders, small_vehicles, matrix)
    vehicle_map = {v.vehicle_id: v for v in small_vehicles}
    order_map = {o.order_id: o for o in small_orders}
    for route in result.routes:
        total = sum(order_map[s.order_id].weight for s in route.stops)
        assert total <= vehicle_map[route.vehicle_id].max_weight


def test_no_route_exceeds_volume_capacity(small_orders, small_vehicles):
    matrix = _matrix(small_orders, small_vehicles)
    result = solver.solve(small_orders, small_vehicles, matrix)
    vehicle_map = {v.vehicle_id: v for v in small_vehicles}
    order_map = {o.order_id: o for o in small_orders}
    for route in result.routes:
        total = sum(order_map[s.order_id].volume for s in route.stops)
        assert total <= vehicle_map[route.vehicle_id].max_volume


# --- unassigned ---

def test_order_unassigned_when_too_heavy():
    heavy_order = make_order("ORD-HEAVY", weight=9999.0, volume=0.1)
    vehicle = make_vehicle(max_weight=100.0, max_volume=2.0)
    matrix = _matrix([heavy_order], [vehicle])
    result = solver.solve([heavy_order], [vehicle], matrix)
    assert "ORD-HEAVY" in result.unassigned_orders


def test_order_unassigned_when_too_voluminous():
    bulky_order = make_order("ORD-BULKY", weight=1.0, volume=99.0)
    vehicle = make_vehicle(max_weight=500.0, max_volume=2.0)
    matrix = _matrix([bulky_order], [vehicle])
    result = solver.solve([bulky_order], [vehicle], matrix)
    assert "ORD-BULKY" in result.unassigned_orders


def test_no_unassigned_with_generous_capacity():
    orders = [make_order(f"ORD-{i:03d}", weight=1.0, volume=0.01) for i in range(10)]
    vehicle = make_vehicle(max_weight=9999.0, max_volume=9999.0)
    matrix = _matrix(orders, [vehicle])
    result = solver.solve(orders, [vehicle], matrix)
    assert result.unassigned_orders == []


# --- edge cases ---

def test_empty_orders_returns_empty_result(small_vehicles):
    result = solver.solve([], small_vehicles, [[0.0]])
    assert result.routes == []
    assert result.unassigned_orders == []
    assert result.total_distance == 0.0


def test_single_order_single_vehicle():
    order = make_order()
    vehicle = make_vehicle()
    matrix = _matrix([order], [vehicle])
    result = solver.solve([order], [vehicle], matrix)
    assert len(result.routes) == 1
    assert result.routes[0].stops[0].order_id == order.order_id