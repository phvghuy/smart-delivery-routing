from dataclasses import dataclass

from smart_delivery_routing.domain.models import Order, RoutingResult, Vehicle
from smart_delivery_routing.domain.ports import DistanceCalculator, RouteSolver
from smart_delivery_routing.domain.validators import ValidationError, validate_orders, validate_vehicles

from .kpi import KPIReport, compute_kpi


@dataclass(frozen=True)
class OptimizeRoutesInput:
    orders: list[Order]
    vehicles: list[Vehicle]


@dataclass(frozen=True)
class OptimizeRoutesOutput:
    result: RoutingResult
    kpi: KPIReport


class ValidationFailed(Exception):
    def __init__(self, errors: list[ValidationError]) -> None:
        self.errors = errors
        super().__init__(f"{len(errors)} validation error(s)")


def optimize_routes(
    input: OptimizeRoutesInput,
    solver: RouteSolver,
    distance_calculator: DistanceCalculator,
) -> OptimizeRoutesOutput:
    _validate(input.orders, input.vehicles)
    distance_matrix = _build_distance_matrix(input.orders, input.vehicles, distance_calculator)
    result = solver.solve(input.orders, input.vehicles, distance_matrix)
    kpi = compute_kpi(result, input.orders, input.vehicles)
    return OptimizeRoutesOutput(result=result, kpi=kpi)


def _validate(orders: list[Order], vehicles: list[Vehicle]) -> None:
    errors = validate_vehicles(vehicles) + validate_orders(orders, vehicles)
    if errors:
        raise ValidationFailed(errors)


def _build_distance_matrix(
    orders: list[Order],
    vehicles: list[Vehicle],
    distance_calculator: DistanceCalculator,
) -> list[list[float]]:
    depot = vehicles[0].depot
    locations = [depot] + [o.location for o in orders]
    return distance_calculator.compute_matrix(locations)
