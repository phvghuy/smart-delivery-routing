from fastapi import FastAPI, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse

from smart_delivery_routing.application.data_loader import LoadError, load_orders_from_bytes, load_vehicles_from_bytes
from smart_delivery_routing.application.use_cases import (
    OptimizeRoutesInput,
    OptimizeRoutesOutput,
    ValidationFailed,
    optimize_routes,
)
from smart_delivery_routing.domain.models import Location, Order, Vehicle
from smart_delivery_routing.infrastructure.distance import HaversineDistanceCalculator
from smart_delivery_routing.application.solvers.nearest_neighbor import NearestNeighborSolver
from smart_delivery_routing.application.solvers.ortools_solver import ORToolsSolver
from smart_delivery_routing.domain.ports import RouteSolver
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
    ("ortools", ORToolsSolver(time_limit_seconds=10)),
]
_distance_calculator = HaversineDistanceCalculator()



# _UI_HTML = """<!DOCTYPE html>
# <html lang="en">
# <head>
#   <meta charset="UTF-8">
#   <title>Smart Delivery Routing</title>
#   <style>
#     * { box-sizing: border-box; }
#     body { font-family: sans-serif; margin: 0; display: flex; flex-direction: column; height: 100vh; }
#     header {
#       padding: 12px 24px; background: #1e3a5f; color: white;
#       display: flex; align-items: center; gap: 20px; flex-shrink: 0; flex-wrap: wrap;
#     }
#     header h1 { font-size: 1rem; margin: 0; white-space: nowrap; }
#     .field { display: flex; flex-direction: column; gap: 2px; }
#     .field label { font-size: 0.75rem; color: #aac; }
#     .field input { font-size: 0.85rem; color: white; background: transparent; border: none; cursor: pointer; }
#     button {
#       background: #2563eb; color: white; border: none;
#       padding: 8px 20px; border-radius: 6px; cursor: pointer; font-size: 0.9rem;
#     }
#     button:disabled { background: #555; cursor: not-allowed; }
#     button:hover:not(:disabled) { background: #1d4ed8; }
#     #status { font-size: 0.85rem; color: #7dd3fc; }
#     #map-frame { flex: 1; border: none; width: 100%; }
#   </style>
# </head>
# <body>
#   <header>
#     <h1>Smart Delivery Routing</h1>
#     <div class="field">
#       <label>Orders CSV</label>
#       <input type="file" id="orders-file" accept=".csv">
#     </div>
#     <div class="field">
#       <label>Vehicles CSV</label>
#       <input type="file" id="vehicles-file" accept=".csv">
#     </div>
#     <button id="btn" onclick="runOptimize()">Optimize &amp; View Map</button>
#     <span id="status"></span>
#   </header>

#   <iframe id="map-frame" srcdoc="<p style='padding:24px;color:#888'>Upload both CSV files and click Optimize.</p>"></iframe>

#   <script>
#     async function runOptimize() {
#       const ordersFile   = document.getElementById('orders-file').files[0];
#       const vehiclesFile = document.getElementById('vehicles-file').files[0];
#       const status = document.getElementById('status');
#       const btn    = document.getElementById('btn');
#       const frame  = document.getElementById('map-frame');

#       if (!ordersFile || !vehiclesFile) {
#         status.textContent = 'Please select both files.';
#         return;
#       }

#       btn.disabled = true;
#       status.textContent = 'Optimizing...';

#       const form = new FormData();
#       form.append('orders_file', ordersFile);
#       form.append('vehicles_file', vehiclesFile);

#       try {
#         const res = await fetch('/optimize/map', { method: 'POST', body: form });
#         if (!res.ok) {
#           const err = await res.json().catch(() => ({}));
#           status.textContent = 'Error: ' + (err.error || res.statusText);
#           return;
#         }
#         frame.srcdoc = await res.text();
#         status.textContent = 'Done.';
#       } catch (e) {
#         status.textContent = 'Request failed.';
#       } finally {
#         btn.disabled = false;
#       }
#     }
#   </script>
# </body>
# </html>"""


# @app.get("/", response_class=HTMLResponse)
# def index() -> HTMLResponse:
#     return HTMLResponse(content=_UI_HTML)


@app.post("/optimize", response_model=OptimizeResponse)
def optimize(request: OptimizeRequest) -> OptimizeResponse:
    input = OptimizeRoutesInput(
        orders=_to_orders(request),
        vehicles=_to_vehicles(request),
    )
    return _run_all_solvers(input)


@app.post("/optimize/upload", response_model=OptimizeResponse)
async def optimize_upload(
    orders_file: UploadFile,
    vehicles_file: UploadFile,
) -> OptimizeResponse:
    orders = load_orders_from_bytes(await orders_file.read(), source=orders_file.filename or "orders")
    vehicles = load_vehicles_from_bytes(await vehicles_file.read(), source=vehicles_file.filename or "vehicles")
    return _run_all_solvers(OptimizeRoutesInput(orders=orders, vehicles=vehicles))


@app.exception_handler(ValidationFailed)
def handle_validation_failed(_, exc: ValidationFailed) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"errors": [{"id": e.entity_id, "field": e.field, "reason": e.reason} for e in exc.errors]},
    )


@app.exception_handler(LoadError)
def handle_load_error(_, exc: LoadError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"error": str(exc)})


# --- Converters: schema → domain ---

def _to_orders(request: OptimizeRequest) -> list[Order]:
    return [
        Order(
            order_id=o.order_id,
            location=Location(lat=o.lat, lng=o.lng),
            weight=o.weight,
            volume=o.volume,
        )
        for o in request.orders
    ]


def _to_vehicles(request: OptimizeRequest) -> list[Vehicle]:
    return [
        Vehicle(
            vehicle_id=v.vehicle_id,
            depot=Location(lat=v.start_lat, lng=v.start_lng),
            max_weight=v.max_weight,
            max_volume=v.max_volume,
        )
        for v in request.vehicles
    ]


# --- Orchestration ---

def _run_all_solvers(input: OptimizeRoutesInput) -> OptimizeResponse:
    return OptimizeResponse(
        results=[
            _to_solver_result(solver_name, optimize_routes(input, solver, _distance_calculator))
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