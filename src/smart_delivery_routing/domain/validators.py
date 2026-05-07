from dataclasses import dataclass

from .models import Order, Vehicle


@dataclass(frozen=True)
class ValidationError:
    entity_id: str
    field: str
    reason: str


# --- Location rules ---

def _check_lat(entity_id: str, field: str, lat: float) -> ValidationError | None:
    if not (-90 <= lat <= 90):
        return ValidationError(entity_id, field, f"invalid latitude {lat}")
    return None


def _check_lng(entity_id: str, field: str, lng: float) -> ValidationError | None:
    if not (-180 <= lng <= 180):
        return ValidationError(entity_id, field, f"invalid longitude {lng}")
    return None


# --- Order rules ---

def _check_order_duplicate_id(order: Order, seen: set[str]) -> ValidationError | None:
    if order.order_id in seen:
        return ValidationError(order.order_id, "order_id", "duplicate order_id")
    return None


def _check_order_weight_positive(order: Order) -> ValidationError | None:
    if order.weight <= 0:
        return ValidationError(order.order_id, "weight", "weight must be positive")
    return None


def _check_order_volume_positive(order: Order) -> ValidationError | None:
    if order.volume <= 0:
        return ValidationError(order.order_id, "volume", "volume must be positive")
    return None


def _check_order_weight_fits_vehicle(order: Order, max_vehicle_weight: float) -> ValidationError | None:
    if order.weight > max_vehicle_weight:
        return ValidationError(
            order.order_id, "weight",
            f"exceeds max vehicle capacity ({max_vehicle_weight})",
        )
    return None


def _check_order_volume_fits_vehicle(order: Order, max_vehicle_volume: float) -> ValidationError | None:
    if order.volume > max_vehicle_volume:
        return ValidationError(
            order.order_id, "volume",
            f"exceeds max vehicle capacity ({max_vehicle_volume})",
        )
    return None


# --- Vehicle rules ---

def _check_vehicle_duplicate_id(vehicle: Vehicle, seen: set[str]) -> ValidationError | None:
    if vehicle.vehicle_id in seen:
        return ValidationError(vehicle.vehicle_id, "vehicle_id", "duplicate vehicle_id")
    return None


def _check_vehicle_max_weight_positive(vehicle: Vehicle) -> ValidationError | None:
    if vehicle.max_weight <= 0:
        return ValidationError(vehicle.vehicle_id, "max_weight", "max_weight must be positive")
    return None


def _check_vehicle_max_volume_positive(vehicle: Vehicle) -> ValidationError | None:
    if vehicle.max_volume <= 0:
        return ValidationError(vehicle.vehicle_id, "max_volume", "max_volume must be positive")
    return None


# --- Public validators ---

def validate_orders(orders: list[Order], vehicles: list[Vehicle]) -> list[ValidationError]:
    errors: list[ValidationError] = []
    max_vehicle_weight = max((v.max_weight for v in vehicles), default=0.0)
    max_vehicle_volume = max((v.max_volume for v in vehicles), default=0.0)
    seen_ids: set[str] = set()

    for order in orders:
        candidates = [
            _check_order_duplicate_id(order, seen_ids),
            _check_lat(order.order_id, "lat", order.location.lat),
            _check_lng(order.order_id, "lng", order.location.lng),
            _check_order_weight_positive(order),
            _check_order_volume_positive(order),
            _check_order_weight_fits_vehicle(order, max_vehicle_weight),
            _check_order_volume_fits_vehicle(order, max_vehicle_volume),
        ]
        errors.extend(e for e in candidates if e is not None)
        seen_ids.add(order.order_id)

    return errors


def validate_vehicles(vehicles: list[Vehicle]) -> list[ValidationError]:
    errors: list[ValidationError] = []
    seen_ids: set[str] = set()

    for vehicle in vehicles:
        candidates = [
            _check_vehicle_duplicate_id(vehicle, seen_ids),
            _check_lat(vehicle.vehicle_id, "depot.lat", vehicle.depot.lat),
            _check_lng(vehicle.vehicle_id, "depot.lng", vehicle.depot.lng),
            _check_vehicle_max_weight_positive(vehicle),
            _check_vehicle_max_volume_positive(vehicle),
        ]
        errors.extend(e for e in candidates if e is not None)
        seen_ids.add(vehicle.vehicle_id)

    return errors
