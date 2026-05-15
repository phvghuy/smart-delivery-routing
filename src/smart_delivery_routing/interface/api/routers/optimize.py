from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from smart_delivery_routing.application.services import DistanceCalculator, JobService, RouteSolver
from smart_delivery_routing.application.use_cases import OptimizeRoutesInput, OptimizeRoutesOutput, optimize_routes
from smart_delivery_routing.domain.repositories import OrderRepository, VehicleRepository, WarehouseRepository
from ..dependencies import get_distance_calculator, get_job_service, get_order_repo, get_solvers, get_vehicle_repo, get_warehouse_repo, require_admin
from ..schemas import AsyncOptimizeResponse, KPIReportResponse, OptimizeResponse, RouteResponse, SolverResultResponse, StopResponse, VehicleKPIResponse

_security = HTTPBearer()

router = APIRouter(tags=["optimize"])


@router.post("/optimize", response_model=OptimizeResponse)
def optimize(
    order_repo: OrderRepository = Depends(get_order_repo),
    vehicle_repo: VehicleRepository = Depends(get_vehicle_repo),
    warehouse_repo: WarehouseRepository = Depends(get_warehouse_repo),
    _: None = Depends(require_admin),
    distance_calculator: DistanceCalculator = Depends(get_distance_calculator),
    solvers: list[tuple[str, RouteSolver]] = Depends(get_solvers),
) -> OptimizeResponse:
    orders = order_repo.get_orders()
    vehicles = vehicle_repo.get_vehicles()
    warehouses = warehouse_repo.get_warehouses()
    return _run_all_solvers(
        OptimizeRoutesInput(orders=orders, vehicles=vehicles, warehouses=warehouses),
        order_repo,
        vehicle_repo,
        distance_calculator,
        solvers,
    )


@router.post("/optimize/async", response_model=AsyncOptimizeResponse, status_code=202)
def optimize_async(
    token=Depends(_security),
    _: None = Depends(require_admin),
    job_service: JobService = Depends(get_job_service),
) -> AsyncOptimizeResponse:
    job_id = job_service.submit(token.credentials)
    return AsyncOptimizeResponse(job_id=job_id)


def _run_all_solvers(
    input: OptimizeRoutesInput,
    order_repo: OrderRepository,
    vehicle_repo: VehicleRepository,
    distance_calculator: DistanceCalculator,
    solvers: list[tuple[str, RouteSolver]],
) -> OptimizeResponse:
    return OptimizeResponse(
        results=[
            _to_solver_result(solver_name, optimize_routes(input, solver, distance_calculator, order_repo, vehicle_repo))
            for solver_name, solver in solvers
        ]
    )


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
