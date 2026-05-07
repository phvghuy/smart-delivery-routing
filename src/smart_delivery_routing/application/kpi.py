from dataclasses import dataclass

from smart_delivery_routing.domain.models import Order, Route, RoutingResult, Vehicle


@dataclass(frozen=True)
class VehicleKPI:
    vehicle_id: str
    stops_count: int
    distance_km: float
    fill_rate_weight: float  # 0.0 – 1.0
    fill_rate_volume: float  # 0.0 – 1.0


@dataclass(frozen=True)
class KPIReport:
    total_distance_km: float
    vehicles_used: int
    unassigned_count: int
    average_fill_rate_weight: float  # 0.0 – 1.0
    average_fill_rate_volume: float  # 0.0 – 1.0
    per_vehicle: list[VehicleKPI]


@dataclass(frozen=True)
class KPIComparison:
    baseline: KPIReport
    optimized: KPIReport
    distance_reduction_pct: float   # positive = improvement
    vehicles_saved: int
    unassigned_delta: int           # negative = fewer unassigned = improvement
    fill_rate_weight_delta: float   # positive = improvement
    fill_rate_volume_delta: float   # positive = improvement


def compute_kpi(
    result: RoutingResult,
    orders: list[Order],
    vehicles: list[Vehicle],
) -> KPIReport:
    order_by_id = {o.order_id: o for o in orders}
    vehicle_map = {v.vehicle_id: v for v in vehicles}

    per_vehicle = [_vehicle_kpi(route, vehicle_map, order_by_id) for route in result.routes]

    avg_fill_weight = (
        sum(v.fill_rate_weight for v in per_vehicle) / len(per_vehicle) if per_vehicle else 0.0
    )
    avg_fill_volume = (
        sum(v.fill_rate_volume for v in per_vehicle) / len(per_vehicle) if per_vehicle else 0.0
    )

    return KPIReport(
        total_distance_km=result.total_distance,
        vehicles_used=result.vehicles_used,
        unassigned_count=len(result.unassigned_orders),
        average_fill_rate_weight=avg_fill_weight,
        average_fill_rate_volume=avg_fill_volume,
        per_vehicle=per_vehicle,
    )


def compare_kpi(baseline: KPIReport, optimized: KPIReport) -> KPIComparison:
    distance_reduction_pct = (
        (baseline.total_distance_km - optimized.total_distance_km) / baseline.total_distance_km * 100
        if baseline.total_distance_km > 0
        else 0.0
    )

    return KPIComparison(
        baseline=baseline,
        optimized=optimized,
        distance_reduction_pct=distance_reduction_pct,
        vehicles_saved=baseline.vehicles_used - optimized.vehicles_used,
        unassigned_delta=optimized.unassigned_count - baseline.unassigned_count,
        fill_rate_weight_delta=optimized.average_fill_rate_weight - baseline.average_fill_rate_weight,
        fill_rate_volume_delta=optimized.average_fill_rate_volume - baseline.average_fill_rate_volume,
    )


def _vehicle_kpi(
    route: Route,
    vehicle_map: dict[str, Vehicle],
    order_by_id: dict[str, Order],
) -> VehicleKPI:
    vehicle = vehicle_map[route.vehicle_id]
    total_weight = sum(order_by_id[s.order_id].weight for s in route.stops)
    total_volume = sum(order_by_id[s.order_id].volume for s in route.stops)

    return VehicleKPI(
        vehicle_id=route.vehicle_id,
        stops_count=len(route.stops),
        distance_km=route.total_distance,
        fill_rate_weight=total_weight / vehicle.max_weight,
        fill_rate_volume=total_volume / vehicle.max_volume,
    )