from ortools.constraint_solver import pywrapcp, routing_enums_pb2

from smart_delivery_routing.domain.models import Order, Route, RoutingResult, Stop, Vehicle
from smart_delivery_routing.application.services import RouteSolver

# OR-Tools works with integers — scale floats before passing in
_DISTANCE_SCALE = 1_000   # km → m
_WEIGHT_SCALE = 100       # kg (2 decimal places)
_VOLUME_SCALE = 1_000     # m³ (3 decimal places)


class ORToolsSolver(RouteSolver):
    def __init__(self, time_limit_seconds: int = 30) -> None:
        self._time_limit = time_limit_seconds

    def solve(
        self,
        orders: list[Order],
        vehicles: list[Vehicle],
        distance_matrix: list[list[float]],
    ) -> RoutingResult:
        if not orders:
            return RoutingResult(routes=[], unassigned_orders=[], total_distance=0.0, vehicles_used=0)

        int_matrix = _scale_matrix(distance_matrix)
        manager = pywrapcp.RoutingIndexManager(len(orders) + 1, len(vehicles), 0)
        routing = pywrapcp.RoutingModel(manager)

        _register_distance(routing, manager, int_matrix)
        _register_weight_capacity(routing, manager, orders, vehicles)
        _register_volume_capacity(routing, manager, orders, vehicles)
        _allow_dropping_orders(routing, manager, orders)

        params = pywrapcp.DefaultRoutingSearchParameters()
        params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        params.time_limit.seconds = self._time_limit

        solution = routing.SolveWithParameters(params)

        if not solution:
            return RoutingResult(
                routes=[],
                unassigned_orders=[o.order_id for o in orders],
                total_distance=0.0,
                vehicles_used=0,
            )

        return _extract_result(solution, routing, manager, orders, vehicles, int_matrix)


# --- Setup helpers ---

def _scale_matrix(matrix: list[list[float]]) -> list[list[int]]:
    return [[int(d * _DISTANCE_SCALE) for d in row] for row in matrix]


def _register_distance(routing, manager, int_matrix: list[list[int]]) -> None:
    def distance_callback(from_index: int, to_index: int) -> int:
        return int_matrix[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]

    idx = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(idx)


def _register_weight_capacity(routing, manager, orders: list[Order], vehicles: list[Vehicle]) -> None:
    def weight_callback(from_index: int) -> int:
        node = manager.IndexToNode(from_index)
        return 0 if node == 0 else int(orders[node - 1].weight * _WEIGHT_SCALE)

    idx = routing.RegisterUnaryTransitCallback(weight_callback)
    routing.AddDimensionWithVehicleCapacity(
        idx,
        0,
        [int(v.max_weight * _WEIGHT_SCALE) for v in vehicles],
        True,
        "Weight",
    )


def _register_volume_capacity(routing, manager, orders: list[Order], vehicles: list[Vehicle]) -> None:
    def volume_callback(from_index: int) -> int:
        node = manager.IndexToNode(from_index)
        return 0 if node == 0 else int(orders[node - 1].volume * _VOLUME_SCALE)

    idx = routing.RegisterUnaryTransitCallback(volume_callback)
    routing.AddDimensionWithVehicleCapacity(
        idx,
        0,
        [int(v.max_volume * _VOLUME_SCALE) for v in vehicles],
        True,
        "Volume",
    )


def _allow_dropping_orders(routing, manager, orders: list[Order]) -> None:
    # High penalty discourages dropping but allows it when capacity is truly insufficient
    penalty = 1_000_000 * _DISTANCE_SCALE
    for node in range(1, len(orders) + 1):
        routing.AddDisjunction([manager.NodeToIndex(node)], penalty)


# --- Solution extraction ---

def _extract_result(
    solution,
    routing,
    manager,
    orders: list[Order],
    vehicles: list[Vehicle],
    int_matrix: list[list[int]],
) -> RoutingResult:
    routes: list[Route] = []
    assigned_ids: set[str] = set()

    for vehicle_idx, vehicle in enumerate(vehicles):
        stops: list[Stop] = []
        distance_scaled = 0
        index = routing.Start(vehicle_idx)

        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            if node != 0:
                order = orders[node - 1]
                stops.append(Stop(order_id=order.order_id, location=order.location))
                assigned_ids.add(order.order_id)
            next_index = solution.Value(routing.NextVar(index))
            distance_scaled += int_matrix[manager.IndexToNode(index)][manager.IndexToNode(next_index)]
            index = next_index

        if stops:
            routes.append(Route(
                vehicle_id=vehicle.vehicle_id,
                stops=stops,
                total_distance=distance_scaled / _DISTANCE_SCALE,
            ))

    unassigned = [o.order_id for o in orders if o.order_id not in assigned_ids]
    return RoutingResult(
        routes=routes,
        unassigned_orders=unassigned,
        total_distance=sum(r.total_distance for r in routes),
        vehicles_used=len(routes),
    )