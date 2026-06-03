from pydantic import BaseModel, Field


# --- Auth ---

class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    role: str


# --- Routing ---

class StopResponse(BaseModel):
    order_id: str
    lat: float
    lng: float


class RouteResponse(BaseModel):
    vehicle_id: str
    stops: list[StopResponse]
    total_distance_km: float
    geometry: list[list[float]] = []  # [[lat, lng], ...] following actual roads


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


class AsyncOptimizeResponse(BaseModel):
    job_id: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str  # pending | success | failure | expired
    result: OptimizeResponse | None = None
    error: str | None = None


# --- Orders CRUD ---

class OrderResponse(BaseModel):
    order_id: str
    warehouse_id: str
    lat: float
    lng: float
    weight: float
    volume: float
    status: str


class PaginatedOrderResponse(BaseModel):
    items: list[OrderResponse]
    total: int
    page: int
    size: int
    pages: int


class CreateOrderRequest(BaseModel):
    order_id: str
    warehouse_id: str
    lat: float
    lng: float
    weight: float = Field(gt=0)
    volume: float = Field(gt=0)


class UpdateOrderRequest(BaseModel):
    warehouse_id: str
    lat: float
    lng: float
    weight: float = Field(gt=0)
    volume: float = Field(gt=0)
    status: str


# --- Hubs CRUD ---

class HubResponse(BaseModel):
    id: str
    name: str
    type: int
    address_text: str
    lat: float
    lng: float
    status: int
    deleted_at: str | None = None


class PaginatedHubResponse(BaseModel):
    items: list[HubResponse]
    total: int
    page: int
    size: int
    pages: int


class CreateHubRequest(BaseModel):
    id: str
    name: str
    type: int
    address_text: str
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)


class UpdateHubRequest(BaseModel):
    name: str
    type: int
    address_text: str
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)
    status: int


# --- Trucks CRUD ---

class TruckResponse(BaseModel):
    id: str
    plate_number: str
    max_weight: float
    max_volume: float
    status: int
    deleted_at: str | None = None


class PaginatedTruckResponse(BaseModel):
    items: list[TruckResponse]
    total: int
    page: int
    size: int
    pages: int


class CreateTruckRequest(BaseModel):
    id: str
    plate_number: str
    max_weight: float = Field(gt=0)
    max_volume: float = Field(gt=0)


class UpdateTruckRequest(BaseModel):
    plate_number: str
    max_weight: float = Field(gt=0)
    max_volume: float = Field(gt=0)
    status: int


# --- Vehicles CRUD ---

class VehicleResponse(BaseModel):
    vehicle_id: str
    current_warehouse_id: str
    max_weight: float
    max_volume: float


class CreateVehicleRequest(BaseModel):
    vehicle_id: str
    current_warehouse_id: str
    max_weight: float = Field(gt=0)
    max_volume: float = Field(gt=0)


class UpdateVehicleRequest(BaseModel):
    current_warehouse_id: str
    max_weight: float = Field(gt=0)
    max_volume: float = Field(gt=0)


# --- Drivers CRUD ---

class DriverResponse(BaseModel):
    id: str
    name: str
    phone: str
    plate_number: str
    current_hub_id: str
    hub_name: str
    max_weight: float
    max_volume: float
    status: int
    fcm_token: str
    deleted_at: str | None = None


class PaginatedDriverResponse(BaseModel):
    items: list[DriverResponse]
    total: int
    page: int
    size: int
    pages: int


class UpdateFCMTokenRequest(BaseModel):
    fcm_token: str


class CreateDriverRequest(BaseModel):
    id: str
    name: str
    phone: str
    plate_number: str
    current_hub_id: str
    max_weight: float = Field(gt=0)
    max_volume: float = Field(gt=0)
    fcm_token: str = ""


class UpdateDriverRequest(BaseModel):
    name: str
    phone: str
    plate_number: str
    current_hub_id: str
    max_weight: float = Field(gt=0)
    max_volume: float = Field(gt=0)
    status: int
    fcm_token: str = ""


# --- Parcels ---

class ParcelResponse(BaseModel):
    id: str
    shipping_request_id: str
    tracking_number: str
    origin_hub_id: str
    origin_hub_name: str
    destination_hub_id: str
    destination_hub_name: str
    current_hub_id: str | None = None
    current_hub_name: str
    weight: float
    volume: float
    status: int
    created_at: str
    updated_at: str


class CursorPagedParcelResponse(BaseModel):
    items: list[ParcelResponse]
    next_cursor: str | None


# --- Shipping Requests ---

class ShippingRequestResponse(BaseModel):
    id: str
    external_order_id: str
    seller_id: str
    pickup_address_text: str
    pickup_lat: float
    pickup_lng: float
    delivery_address_text: str
    delivery_lat: float
    delivery_lng: float
    receiver_name: str
    receiver_phone: str
    weight: float
    volume: float
    service_type: int
    status: int
    cod_amount: float | None = None
    cod_currency: str | None = None
    created_at: str


class CursorPagedShippingRequestResponse(BaseModel):
    items: list[ShippingRequestResponse]
    next_cursor: str | None


class CreateShippingRequestRequest(BaseModel):
    id: str
    external_order_id: str
    seller_id: str
    pickup_address_text: str
    pickup_lat: float = Field(ge=-90, le=90)
    pickup_lng: float = Field(ge=-180, le=180)
    delivery_address_text: str
    delivery_lat: float = Field(ge=-90, le=90)
    delivery_lng: float = Field(ge=-180, le=180)
    receiver_name: str
    receiver_phone: str
    weight: float = Field(gt=0)
    volume: float = Field(gt=0)
    service_type: int = 1
    cod_amount: float | None = None
    cod_currency: str = "VND"


# --- Warehouses CRUD ---

class WarehouseResponse(BaseModel):
    warehouse_id: str
    name: str
    lat: float
    lng: float


class CreateWarehouseRequest(BaseModel):
    warehouse_id: str
    name: str
    lat: float
    lng: float


class UpdateWarehouseRequest(BaseModel):
    name: str
    lat: float
    lng: float
