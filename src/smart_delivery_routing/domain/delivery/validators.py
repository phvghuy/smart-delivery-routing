from ..shared.validators import ValidationError, _check_non_negative, _check_not_empty, _check_phone, _check_positive
from .models import DeliveryRoute, Driver, RouteStop, RouteStopStatus


def validate_driver(driver: Driver) -> list[ValidationError]:
    entity_id = str(driver.id)
    candidates = [
        _check_not_empty(entity_id, "profile.name", driver.profile.name),
        _check_phone(entity_id, "profile.phone", driver.profile.phone),
        _check_not_empty(entity_id, "profile.plate_number", driver.profile.plate_number),
        _check_positive(entity_id, "capacity.max_weight", driver.capacity.max_weight),
        _check_positive(entity_id, "capacity.max_volume", driver.capacity.max_volume),
    ]
    return [e for e in candidates if e is not None]


def validate_delivery_route(route: DeliveryRoute) -> list[ValidationError]:
    entity_id = str(route.id)
    candidates = [_check_non_negative(entity_id, "total_distance_km", route.total_distance_km)]
    return [e for e in candidates if e is not None]


def validate_route_stop(stop: RouteStop) -> list[ValidationError]:
    entity_id = str(stop.id)
    errors: list[ValidationError] = []

    if stop.sequence < 1:
        errors.append(ValidationError(entity_id, "sequence", "sequence must be >= 1"))

    if stop.failed_reason is not None and stop.status != RouteStopStatus.FAILED:
        errors.append(ValidationError(entity_id, "failed_reason", "failed_reason only allowed when status is FAILED"))

    if stop.completed_at is not None and stop.status != RouteStopStatus.DELIVERED:
        errors.append(ValidationError(entity_id, "completed_at", "completed_at only allowed when status is DELIVERED"))

    return errors
