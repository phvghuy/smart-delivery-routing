import pytest

from smart_delivery_routing.application.kpi import KPIReport, compare_kpi, compute_kpi
from smart_delivery_routing.application.solvers.nearest_neighbor import NearestNeighborSolver
from smart_delivery_routing.infrastructure.haversine import HaversineDistanceCalculator
from tests.conftest import make_warehouse

solver = NearestNeighborSolver()
calculator = HaversineDistanceCalculator()


def _run(orders, vehicles, warehouses=None):
    if warehouses is None:
        warehouses = [make_warehouse()]
    locations = [w.location for w in warehouses] + [o.location for o in orders]
    matrix = calculator.compute_matrix(locations)
    return solver.solve(orders, vehicles, warehouses, matrix)


def test_kpi_vehicles_used(small_orders, small_vehicles, small_warehouses):
    result = _run(small_orders, small_vehicles, small_warehouses)
    kpi = compute_kpi(result, small_orders, small_vehicles)
    assert kpi.vehicles_used == result.vehicles_used


def test_kpi_total_distance(small_orders, small_vehicles, small_warehouses):
    result = _run(small_orders, small_vehicles, small_warehouses)
    kpi = compute_kpi(result, small_orders, small_vehicles)
    assert kpi.total_distance_km == pytest.approx(result.total_distance)


def test_kpi_unassigned_count(small_orders, small_vehicles, small_warehouses):
    result = _run(small_orders, small_vehicles, small_warehouses)
    kpi = compute_kpi(result, small_orders, small_vehicles)
    assert kpi.unassigned_count == len(result.unassigned_orders)


def test_kpi_fill_rate_between_0_and_1(small_orders, small_vehicles, small_warehouses):
    result = _run(small_orders, small_vehicles, small_warehouses)
    kpi = compute_kpi(result, small_orders, small_vehicles)
    assert 0.0 <= kpi.average_fill_rate_weight <= 1.0
    assert 0.0 <= kpi.average_fill_rate_volume <= 1.0


def test_kpi_per_vehicle_count(small_orders, small_vehicles, small_warehouses):
    result = _run(small_orders, small_vehicles, small_warehouses)
    kpi = compute_kpi(result, small_orders, small_vehicles)
    assert len(kpi.per_vehicle) == result.vehicles_used


def test_kpi_empty_result_returns_zeros(small_vehicles, small_warehouses):
    result = _run([], small_vehicles, small_warehouses)
    kpi = compute_kpi(result, [], small_vehicles)
    assert kpi.total_distance_km == 0.0
    assert kpi.vehicles_used == 0
    assert kpi.average_fill_rate_weight == 0.0
    assert kpi.average_fill_rate_volume == 0.0


# --- compare_kpi ---

def _make_report(total_distance, vehicles_used, unassigned, fw, fv) -> KPIReport:
    return KPIReport(
        total_distance_km=total_distance,
        vehicles_used=vehicles_used,
        unassigned_count=unassigned,
        average_fill_rate_weight=fw,
        average_fill_rate_volume=fv,
        per_vehicle=[],
    )


def test_compare_distance_reduction():
    baseline = _make_report(1000.0, 5, 0, 0.6, 0.7)
    optimized = _make_report(800.0, 4, 0, 0.75, 0.85)
    cmp = compare_kpi(baseline, optimized)
    assert cmp.distance_reduction_pct == pytest.approx(20.0)


def test_compare_vehicles_saved():
    baseline = _make_report(1000.0, 5, 0, 0.6, 0.7)
    optimized = _make_report(800.0, 4, 0, 0.75, 0.85)
    cmp = compare_kpi(baseline, optimized)
    assert cmp.vehicles_saved == 1


def test_compare_fill_rate_delta():
    baseline = _make_report(1000.0, 5, 0, 0.6, 0.7)
    optimized = _make_report(800.0, 5, 0, 0.75, 0.85)
    cmp = compare_kpi(baseline, optimized)
    assert cmp.fill_rate_weight_delta == pytest.approx(0.15)
    assert cmp.fill_rate_volume_delta == pytest.approx(0.15)


def test_compare_zero_baseline_distance():
    baseline = _make_report(0.0, 0, 0, 0.0, 0.0)
    optimized = _make_report(500.0, 3, 0, 0.5, 0.5)
    cmp = compare_kpi(baseline, optimized)
    assert cmp.distance_reduction_pct == 0.0
