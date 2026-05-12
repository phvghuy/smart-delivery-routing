from fastapi import FastAPI, UploadFile, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from smart_delivery_routing.application.data_loader import LoadError, load_orders_from_bytes, load_vehicles_from_bytes, load_warehouses_from_bytes
from smart_delivery_routing.application.use_cases import (
    OptimizeRoutesInput,
    OptimizeRoutesOutput,
    ValidationFailed,
    optimize_routes,
)
from smart_delivery_routing.domain.models import Location, Order, Vehicle
from smart_delivery_routing.infrastructure.osrm.distance import OSRMDistanceCalculator
from smart_delivery_routing.infrastructure.supabase.client import get_supabase_client
from smart_delivery_routing.infrastructure.supabase.repositories.orders import SupabaseOrderRepository
from smart_delivery_routing.infrastructure.supabase.repositories.vehicles import SupabaseVehicleRepository
from smart_delivery_routing.infrastructure.supabase.repositories.warehouses import SupabaseWarehouseRepository
from smart_delivery_routing.application.solvers.nearest_neighbor import NearestNeighborSolver
from smart_delivery_routing.application.solvers.ortools_solver import ORToolsSolver
from smart_delivery_routing.domain.ports import RouteSolver, OrderRepository, VehicleRepository, WarehouseRepository
from .visualizer import build_map

from .schemas import (
    OptimizeRequest,
    OptimizeResponse,
    KPIReportResponse,
    RouteResponse,
    SolverResultResponse,
    StopResponse,
    VehicleKPIResponse,
)

app = FastAPI(title="Smart Delivery Routing")

_SOLVERS: list[tuple[str, RouteSolver]] = [
    ("nearest_neighbor", NearestNeighborSolver()),
    # ("ortools", ORToolsSolver(time_limit_seconds=10)),
]
_distance_calculator = OSRMDistanceCalculator()


_supabase = get_supabase_client()


def get_order_repo() -> OrderRepository:
    return SupabaseOrderRepository(_supabase)


def get_vehicle_repo() -> VehicleRepository:
    return SupabaseVehicleRepository(_supabase)


def get_warehouse_repo() -> WarehouseRepository:
    return SupabaseWarehouseRepository(_supabase)


@app.post("/import/upload", status_code=201)
async def import_upload(
    orders_file: UploadFile,
    vehicles_file: UploadFile,
    warehouses_file: UploadFile,
    order_repo: OrderRepository = Depends(get_order_repo),
    vehicle_repo: VehicleRepository = Depends(get_vehicle_repo),
    warehouse_repo: WarehouseRepository = Depends(get_warehouse_repo)
) -> dict:
    orders = load_orders_from_bytes(await orders_file.read(), source=orders_file.filename or "orders")
    vehicles = load_vehicles_from_bytes(await vehicles_file.read(), source=vehicles_file.filename or "vehicles")
    warehouses = load_warehouses_from_bytes(await warehouses_file.read(), source=warehouses_file.filename or "warehouses")
    order_repo.save_orders(orders)
    vehicle_repo.save_vehicles(vehicles)
    warehouse_repo.save_warehouses(warehouses)
    return {"imported_orders": len(orders), "imported_vehicles": len(vehicles), "imported_warehouses": len(warehouses)}


@app.post("/optimize", response_model=OptimizeResponse)
def optimize(
    order_repo: OrderRepository = Depends(get_order_repo),
    vehicle_repo: VehicleRepository = Depends(get_vehicle_repo),
    warehouse_repo: WarehouseRepository = Depends(get_warehouse_repo)
) -> OptimizeResponse:
    orders = order_repo.get_pending_orders()
    vehicles = vehicle_repo.get_vehicles()
    warehouses = warehouse_repo.get_warehouses()
    return _run_all_solvers(
        OptimizeRoutesInput(orders=orders, vehicles=vehicles, warehouses=warehouses),
        order_repo,
        vehicle_repo,
    )


@app.exception_handler(ValidationFailed)
def handle_validation_failed(_, exc: ValidationFailed) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"errors": [{"id": e.entity_id, "field": e.field, "reason": e.reason} for e in exc.errors]},
    )


@app.exception_handler(LoadError)
def handle_load_error(_, exc: LoadError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"error": str(exc)})


# --- Orchestration ---

def _run_all_solvers(
    input: OptimizeRoutesInput,
    order_repo: OrderRepository,
    vehicle_repo: VehicleRepository,
) -> OptimizeResponse:
    return OptimizeResponse(
        results=[
            _to_solver_result(solver_name, optimize_routes(input, solver, _distance_calculator, order_repo, vehicle_repo))
            for solver_name, solver in _SOLVERS
        ]
    )


# --- Converters: domain → schema ---

def _to_solver_result(solver_name: str, output: OptimizeRoutesOutput) -> SolverResultResponse:
    return SolverResultResponse(
        solver=solver_name,
        routes=[
            RouteResponse(
                vehicle_id=r.vehicle_id,
                stops=[StopResponse(order_id=s.order_id, lat=s.location.lat, lng=s.location.lng) for s in r.stops],
                total_distance_km=r.total_distance,
            )
            for r in output.result.routes
        ],
        unassigned_orders=output.result.unassigned_orders,
        kpi=KPIReportResponse(
            total_distance_km=output.kpi.total_distance_km,
            vehicles_used=output.kpi.vehicles_used,
            unassigned_count=output.kpi.unassigned_count,
            average_fill_rate_weight=output.kpi.average_fill_rate_weight,
            average_fill_rate_volume=output.kpi.average_fill_rate_volume,
            per_vehicle=[
                VehicleKPIResponse(
                    vehicle_id=v.vehicle_id,
                    stops_count=v.stops_count,
                    distance_km=v.distance_km,
                    fill_rate_weight=v.fill_rate_weight,
                    fill_rate_volume=v.fill_rate_volume,
                )
                for v in output.kpi.per_vehicle
            ],
        ),
    )