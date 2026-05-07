from pydantic import BaseModel, Field


# --- Request ---

class OrderRequest(BaseModel):
    order_id: str
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)
    weight: float = Field(gt=0)
    volume: float = Field(gt=0)


class VehicleRequest(BaseModel):
    vehicle_id: str
    max_weight: float = Field(gt=0)
    max_volume: float = Field(gt=0)
    start_lat: float = Field(ge=-90, le=90)
    start_lng: float = Field(ge=-180, le=180)


class OptimizeRequest(BaseModel):
    orders: list[OrderRequest] = Field(min_length=1)
    vehicles: list[VehicleRequest] = Field(min_length=1)


# --- Response ---

class StopResponse(BaseModel):
    order_id: str
    lat: float
    lng: float


class RouteResponse(BaseModel):
    vehicle_id: str
    stops: list[StopResponse]
    total_distance_km: float


class VehicleKPIResponse(BaseModel):
    vehicle_id: str
    stops_count: int
    distance_km: float
    fill_rate_weight: float
    fill_rate_volume: float


class KPIReportResponse(BaseModel):
    total_distance_km: float
    vehicles_used: int
    unassigned_count: int
    average_fill_rate_weight: float
    average_fill_rate_volume: float
    per_vehicle: list[VehicleKPIResponse]


class SolverResultResponse(BaseModel):
    solver: str
    routes: list[RouteResponse]
    unassigned_orders: list[str]
    kpi: KPIReportResponse


class OptimizeResponse(BaseModel):
    results: list[SolverResultResponse]