import re
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ValidationError:
    entity_id: str
    field: str
    reason: str


def _check_lat(entity_id: str, field: str, lat: float) -> ValidationError | None:
    if not (-90 <= lat <= 90):
        return ValidationError(entity_id, field, f"invalid latitude {lat}")
    return None


def _check_lng(entity_id: str, field: str, lng: float) -> ValidationError | None:
    if not (-180 <= lng <= 180):
        return ValidationError(entity_id, field, f"invalid longitude {lng}")
    return None


def _check_not_empty(entity_id: str, field: str, value: str) -> ValidationError | None:
    if not value.strip():
        return ValidationError(entity_id, field, f"{field} must not be empty")
    return None


def _check_positive(entity_id: str, field: str, value: float) -> ValidationError | None:
    if value <= 0:
        return ValidationError(entity_id, field, f"{field} must be positive")
    return None


def _check_non_negative(entity_id: str, field: str, value: float) -> ValidationError | None:
    if value < 0:
        return ValidationError(entity_id, field, f"{field} must be non-negative")
    return None


def _check_phone(entity_id: str, field: str, phone: str) -> ValidationError | None:
    if not re.match(r"^(0|\+84)\d{9}$", phone):
        return ValidationError(entity_id, field, f"invalid phone number: {phone}")
    return None


def _check_different_hubs(entity_id: str, origin_hub_id: UUID, destination_hub_id: UUID) -> ValidationError | None:
    if origin_hub_id == destination_hub_id:
        return ValidationError(entity_id, "origin_hub_id", "origin and destination hubs must differ")
    return None
