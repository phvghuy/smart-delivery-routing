from smart_delivery_routing.domain.models import Order, Route, RoutingResult, Stop, Vehicle, Warehouse
from smart_delivery_routing.domain.ports import RouteSolver


class NearestNeighborSolver(RouteSolver):
    def solve(
        self,
        orders: list[Order],
        vehicles: list[Vehicle],
        warehouses: list[Warehouse],
        distance_matrix: list[list[float]],
    ) -> RoutingResult:
        unassigned = list(orders)
        routes: list[Route] = []
        warehouse_to_idx = {w.warehouse_id: i for i, w in enumerate(warehouses)}
        order_to_idx = {o.order_id: i + len(warehouses) for i, o in enumerate(orders)}

        for vehicle in vehicles:
            if not unassigned:
                break

            route = Route(vehicle_id=vehicle.vehicle_id)
            remaining_weight = vehicle.max_weight
            remaining_volume = vehicle.max_volume
            current_index = warehouse_to_idx[vehicle.current_warehouse_id]

            while unassigned:
                candidate = _nearest_fitting(
                    current_index=current_index,
                    candidates=unassigned,
                    order_to_idx=order_to_idx,
                    distance_matrix=distance_matrix,
                    remaining_weight=remaining_weight,
                    remaining_volume=remaining_volume,
                )
                if candidate is None:
                    break

                order_index = order_to_idx[candidate.order_id]
                route.total_distance += distance_matrix[current_index][order_index]
                route.stops.append(Stop(order_id=candidate.order_id, location=candidate.location))
                remaining_weight -= candidate.weight
                remaining_volume -= candidate.volume
                current_index = order_index
                unassigned.remove(candidate)

            if route.stops:
                vehicle.current_warehouse_id = _nearest_warehouse_with_orders(
                    current_index=current_index,
                    warehouses=warehouses,
                    warehouse_to_idx=warehouse_to_idx,
                    distance_matrix=distance_matrix,
                    unassigned=unassigned,
                ).warehouse_id
                route.total_distance += distance_matrix[current_index][warehouse_to_idx[vehicle.current_warehouse_id]]
                routes.append(route)

        return RoutingResult(
            routes=routes,
            unassigned_orders=[o.order_id for o in unassigned],
            total_distance=sum(r.total_distance for r in routes),
            vehicles_used=len(routes),
        )


def _nearest_fitting(
    current_index: int,
    candidates: list[Order],
    order_to_idx: dict[str, int],
    distance_matrix: list[list[float]],
    remaining_weight: float,
    remaining_volume: float,
) -> Order | None:
    best: Order | None = None
    best_distance = float("inf")

    for order in candidates:
        if order.weight > remaining_weight or order.volume > remaining_volume:
            continue
        order_index = order_to_idx[order.order_id]
        d = distance_matrix[current_index][order_index]
        if d < best_distance:
            best_distance = d
            best = order

    return best

def _nearest_warehouse_with_orders(
    current_index: int,
    warehouses: list[Warehouse],
    warehouse_to_idx: dict[str, int],
    distance_matrix: list[list[float]],
    unassigned: list[Order],
) -> Warehouse:
    warehouses_with_orders = {o.warehouse_id for o in unassigned}
    candidates = [w for w in warehouses if w.warehouse_id in warehouses_with_orders] or warehouses
    return min(candidates, key=lambda w: distance_matrix[current_index][warehouse_to_idx[w.warehouse_id]])
