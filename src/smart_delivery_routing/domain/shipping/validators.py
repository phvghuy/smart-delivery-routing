from ..shared.validators import (
    ValidationError,
    _check_lat,
    _check_lng,
    _check_non_negative,
    _check_not_empty,
    _check_phone,
    _check_positive,
)
from .models import ShippingRequest


def validate_shipping_request(request: ShippingRequest) -> list[ValidationError]:
    entity_id = str(request.id)
    candidates = [
        _check_not_empty(entity_id, "external_order_id", request.external_order_id),
        _check_not_empty(entity_id, "pickup_address.text", request.pickup_address.text),
        _check_lat(entity_id, "pickup_address.lat", request.pickup_address.location.lat),
        _check_lng(entity_id, "pickup_address.lng", request.pickup_address.location.lng),
        _check_not_empty(entity_id, "delivery_address.text", request.delivery_address.text),
        _check_lat(entity_id, "delivery_address.lat", request.delivery_address.location.lat),
        _check_lng(entity_id, "delivery_address.lng", request.delivery_address.location.lng),
        _check_not_empty(entity_id, "receiver.name", request.receiver.name),
        _check_phone(entity_id, "receiver.phone", request.receiver.phone),
        _check_positive(entity_id, "load.weight", request.load.weight),
        _check_positive(entity_id, "load.volume", request.load.volume),
    ]
    if request.cod_amount is not None:
        candidates.append(_check_non_negative(entity_id, "cod_amount.amount", request.cod_amount.amount))
    return [e for e in candidates if e is not None]
