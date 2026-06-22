from datetime import datetime, timezone
from uuid import uuid4

from smart_delivery_routing.domain.shipping import ShippingRequest, ShippingRequestStatus, ServiceLevel
from smart_delivery_routing.domain.shipping.models import Receiver
from smart_delivery_routing.domain.shipping.validators import validate_shipping_request
from smart_delivery_routing.domain.shared import Address, Load, Location, Money


def _make_request(**overrides) -> ShippingRequest:
    defaults = dict(
        id=uuid4(),
        external_order_id="ORD-001",
        seller_id=uuid4(),
        pickup_address=Address(text="123 Nguyen Hue, Q1", location=Location(lat=10.78, lng=106.70)),
        delivery_address=Address(text="456 Le Loi, Q3", location=Location(lat=10.80, lng=106.72)),
        receiver=Receiver(name="Nguyen Van A", phone="0901234567"),
        load=Load(weight=2.0, volume=0.05),
        created_at=datetime.now(timezone.utc),
        service_type=ServiceLevel.STANDARD,
        cod_amount=None,
        status=ShippingRequestStatus.CREATED,
    )
    return ShippingRequest(**{**defaults, **overrides})


def test_validate_shipping_request_valid():
    assert validate_shipping_request(_make_request()) == []

def test_validate_shipping_request_empty_order_id():
    errors = validate_shipping_request(_make_request(external_order_id=""))
    assert any(e.field == "external_order_id" for e in errors)

def test_validate_shipping_request_empty_pickup_text():
    bad = Address(text="", location=Location(lat=10.78, lng=106.70))
    errors = validate_shipping_request(_make_request(pickup_address=bad))
    assert any(e.field == "pickup_address.text" for e in errors)

def test_validate_shipping_request_invalid_pickup_lat():
    bad = Address(text="abc", location=Location(lat=999.0, lng=106.70))
    errors = validate_shipping_request(_make_request(pickup_address=bad))
    assert any(e.field == "pickup_address.lat" for e in errors)

def test_validate_shipping_request_invalid_pickup_lng():
    bad = Address(text="abc", location=Location(lat=10.78, lng=999.0))
    errors = validate_shipping_request(_make_request(pickup_address=bad))
    assert any(e.field == "pickup_address.lng" for e in errors)

def test_validate_shipping_request_invalid_delivery_lat():
    bad = Address(text="abc", location=Location(lat=-999.0, lng=106.70))
    errors = validate_shipping_request(_make_request(delivery_address=bad))
    assert any(e.field == "delivery_address.lat" for e in errors)

def test_validate_shipping_request_empty_receiver_name():
    errors = validate_shipping_request(_make_request(receiver=Receiver(name="", phone="0901234567")))
    assert any(e.field == "receiver.name" for e in errors)

def test_validate_shipping_request_invalid_phone():
    errors = validate_shipping_request(_make_request(receiver=Receiver(name="A", phone="12345")))
    assert any(e.field == "receiver.phone" for e in errors)

def test_validate_shipping_request_zero_weight():
    errors = validate_shipping_request(_make_request(load=Load(weight=0.0, volume=0.05)))
    assert any(e.field == "load.weight" for e in errors)

def test_validate_shipping_request_zero_volume():
    errors = validate_shipping_request(_make_request(load=Load(weight=2.0, volume=0.0)))
    assert any(e.field == "load.volume" for e in errors)

def test_validate_shipping_request_negative_cod():
    errors = validate_shipping_request(_make_request(cod_amount=Money(amount=-1)))
    assert any(e.field == "cod_amount.amount" for e in errors)

def test_validate_shipping_request_none_cod_is_valid():
    assert validate_shipping_request(_make_request(cod_amount=None)) == []

def test_validate_shipping_request_zero_cod_is_valid():
    assert validate_shipping_request(_make_request(cod_amount=Money(amount=0))) == []
