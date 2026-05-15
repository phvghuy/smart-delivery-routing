from smart_delivery_routing.application.solvers.nearest_neighbor import NearestNeighborSolver
from smart_delivery_routing.application.routing_use_cases import NoPendingOrders, OptimizeRoutesInput, optimize_routes
from smart_delivery_routing.config import OSRM_URL
from smart_delivery_routing.infrastructure.celery import celery_app
from smart_delivery_routing.infrastructure.osrm.distance import OSRMDistanceCalculator
from smart_delivery_routing.infrastructure.osrm.geometry import get_road_geometry
from smart_delivery_routing.infrastructure.supabase.client import get_supabase_client
from smart_delivery_routing.infrastructure.supabase.repositories.orders import SupabaseOrderRepository
from smart_delivery_routing.infrastructure.supabase.repositories.vehicles import SupabaseVehicleRepository
from smart_delivery_routing.infrastructure.supabase.repositories.warehouses import SupabaseWarehouseRepository

_solver = NearestNeighborSolver()
_distance_calculator = OSRMDistanceCalculator(base_url=OSRM_URL)


def _build_geometry(vehicle_id, stops, vehicle_start_warehouse, vehicle_end_warehouse, warehouse_map):
    if not stops:
        return []
    start_wh = warehouse_map.get(vehicle_start_warehouse.get(vehicle_id, ""))
    end_wh = warehouse_map.get(vehicle_end_warehouse.get(vehicle_id, ""))
    waypoints = []
    if start_wh:
        waypoints.append((start_wh.location.lat, start_wh.location.lng))
    waypoints.extend((s.location.lat, s.location.lng) for s in stops)
    if end_wh:
        waypoints.append((end_wh.location.lat, end_wh.location.lng))
    return get_road_geometry(waypoints)


@celery_app.task(name="optimize", throws=(NoPendingOrders,))
def run_optimize(token: str) -> dict:
    client = get_supabase_client()
    client.postgrest.auth(token)

    order_repo = SupabaseOrderRepository(client)
    vehicle_repo = SupabaseVehicleRepository(client)
    warehouse_repo = SupabaseWarehouseRepository(client)

    orders = order_repo.get_orders()
    vehicles = vehicle_repo.get_vehicles()
    warehouses = warehouse_repo.get_warehouses()

    # Capture before solver mutates vehicle.current_warehouse_id
    vehicle_start_warehouse = {v.vehicle_id: v.current_warehouse_id for v in vehicles}
    warehouse_map = {w.warehouse_id: w for w in warehouses}

    output = optimize_routes(
        OptimizeRoutesInput(orders=orders, vehicles=vehicles, warehouses=warehouses),
        _solver,
        _distance_calculator,
        order_repo,
        vehicle_repo,
    )

    # After optimize_routes, vehicles are mutated — current_warehouse_id is now the ending warehouse
    vehicle_end_warehouse = {v.vehicle_id: v.current_warehouse_id for v in vehicles}

    return {
        "results": [
            {
                "solver": "nearest_neighbor",
                "routes": [
                    {
                        "vehicle_id": r.vehicle_id,
                        "stops": [{"order_id": s.order_id, "lat": s.location.lat, "lng": s.location.lng} for s in r.stops],
                        "total_distance_km": r.total_distance,
                        "geometry": _build_geometry(r.vehicle_id, r.stops, vehicle_start_warehouse, vehicle_end_warehouse, warehouse_map),
                    }
                    for r in output.result.routes
                ],
                "unassigned_orders": output.result.unassigned_orders,
                "kpi": {
                    "total_distance_km": output.kpi.total_distance_km,
                    "vehicles_used": output.kpi.vehicles_used,
                    "unassigned_count": output.kpi.unassigned_count,
                    "average_fill_rate_weight": output.kpi.average_fill_rate_weight,
                    "average_fill_rate_volume": output.kpi.average_fill_rate_volume,
                    "per_vehicle": [
                        {
                            "vehicle_id": v.vehicle_id,
                            "stops_count": v.stops_count,
                            "distance_km": v.distance_km,
                            "fill_rate_weight": v.fill_rate_weight,
                            "fill_rate_volume": v.fill_rate_volume,
                        }
                        for v in output.kpi.per_vehicle
                    ],
                },
            }
        ]
    }
