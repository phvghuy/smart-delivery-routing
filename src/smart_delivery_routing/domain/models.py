from dataclasses import dataclass, field


@dataclass(frozen=True)
class Location:
    lat: float
    lng: float


@dataclass(frozen=True)
class Order:
    order_id: str
    location: Location
    weight: float
    volume: float


@dataclass(frozen=True)
class Vehicle:
    vehicle_id: str
    depot: Location
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
