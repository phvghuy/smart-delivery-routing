from dataclasses import dataclass, field
from enum import Enum


@dataclass(frozen=True)
class Location:
    lat: float
    lng: float


@dataclass(frozen=True)
class Warehouse:
    warehouse_id: str
    location: Location
    name: str = ""


class OrderStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


@dataclass
class Order:
    order_id: str
    warehouse_id: str
    location: Location
    weight: float
    volume: float
    status: OrderStatus = OrderStatus.PENDING
    optimization_job_id: str | None = None


@dataclass
class Vehicle:
    vehicle_id: str
    current_warehouse_id: str
    max_weight: float
    max_volume: float


@dataclass(frozen=True)
class Stop:
    order_id: str
    location: Location


@dataclass
class Route:
    vehicle_id: str
    stops: list[Stop] = field(default_factory=list)
    total_distance: float = 0.0


@dataclass
class RoutingResult:
    routes: list[Route]
    unassigned_orders: list[str]
    total_distance: float
    vehicles_used: int


@dataclass
class Driver:
    driver_id: str
    vehicle_id: str | None = None
    fcm_token: str | None = None


@dataclass
class Notification:
    driver_id: str
    title: str
    body: str
    data: dict
    notification_id: str = ""
    is_read: bool = False
    created_at: str = ""
