from smart_delivery_routing.domain.models import Order, Route, RoutingResult, Stop, Vehicle
from smart_delivery_routing.domain.ports import RouteSolver


class NearestNeighborSolver(RouteSolver):
    def solve(
        self,
        orders: list[Order],
        vehicles: list[Vehicle],
        distance_matrix: list[list[float]],
    ) -> RoutingResult:
        # distance_matrix layout: index 0 = depot, index 1..N = orders (same order as `orders`)
        unassigned = list(orders)
        routes: list[Route] = []
        order_to_idx = {o.order_id: i + 1 for i, o in enumerate(orders)}

        for vehicle in vehicles:
            if not unassigned:
                break

            route = Route(vehicle_id=vehicle.vehicle_id)
            remaining_weight = vehicle.max_weight
            remaining_volume = vehicle.max_volume
            current_index = 0  # depot

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
                route.total_distance += distance_matrix[current_index][0]  # return to depot
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
