from ..shared.validators import (
    ValidationError,
    _check_different_hubs,
    _check_lat,
    _check_lng,
    _check_not_empty,
    _check_positive,
)
from .models import Hub, Parcel, Truck, TruckTrip, TruckTripItem


def validate_hub(hub: Hub) -> list[ValidationError]:
    entity_id = str(hub.id)
    candidates = [
        _check_not_empty(entity_id, "name", hub.name),
        _check_not_empty(entity_id, "address.text", hub.address.text),
        _check_lat(entity_id, "address.lat", hub.address.location.lat),
        _check_lng(entity_id, "address.lng", hub.address.location.lng),
    ]
    return [e for e in candidates if e is not None]


def validate_parcel(parcel: Parcel) -> list[ValidationError]:
    entity_id = str(parcel.id)
    candidates = [
        _check_not_empty(entity_id, "tracking_number", parcel.tracking_number),
        _check_different_hubs(entity_id, parcel.origin_hub_id, parcel.destination_hub_id),
        _check_positive(entity_id, "load.weight", parcel.load.weight),
        _check_positive(entity_id, "load.volume", parcel.load.volume),
    ]
    return [e for e in candidates if e is not None]


def validate_truck(truck: Truck) -> list[ValidationError]:
    entity_id = str(truck.id)
    candidates = [
        _check_not_empty(entity_id, "plate_number", truck.plate_number),
        _check_positive(entity_id, "capacity.max_weight", truck.capacity.max_weight),
        _check_positive(entity_id, "capacity.max_volume", truck.capacity.max_volume),
    ]
    return [e for e in candidates if e is not None]


def validate_truck_trip(trip: TruckTrip) -> list[ValidationError]:
    entity_id = str(trip.id)
    errors = [_check_different_hubs(entity_id, trip.origin_hub_id, trip.destination_hub_id)]

    if trip.actual_departure_time is not None and trip.actual_departure_time < trip.planned_departure_time:
        errors.append(ValidationError(entity_id, "actual_departure_time", "actual departure must be >= planned departure"))

    if trip.actual_arrival_time is not None and trip.actual_departure_time is not None:
        if trip.actual_arrival_time < trip.actual_departure_time:
            errors.append(ValidationError(entity_id, "actual_arrival_time", "arrival must be >= departure"))

    return [e for e in errors if e is not None]


def validate_truck_trip_item(item: TruckTripItem) -> list[ValidationError]:
    if item.unloaded_at is not None and item.unloaded_at < item.loaded_at:
        return [ValidationError(str(item.id), "unloaded_at", "unloaded_at must be >= loaded_at")]
    return []
