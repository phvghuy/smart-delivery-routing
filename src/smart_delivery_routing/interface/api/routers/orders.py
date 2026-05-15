from fastapi import APIRouter, Depends

from smart_delivery_routing.application import order_use_cases
from smart_delivery_routing.domain.models import Location, Order, OrderStatus
from smart_delivery_routing.domain.repositories import OrderRepository
from ..dependencies import get_order_repo, require_admin, require_driver
from ..schemas import CreateOrderRequest, OrderResponse, UpdateOrderRequest

router = APIRouter(prefix="/orders", tags=["orders"])


def _to_response(order: Order) -> OrderResponse:
    return OrderResponse(
        order_id=order.order_id,
        warehouse_id=order.warehouse_id,
        lat=order.location.lat,
        lng=order.location.lng,
        weight=order.weight,
        volume=order.volume,
        status=order.status.value,
    )


@router.get("", response_model=list[OrderResponse])
def list_orders(
    order_repo: OrderRepository = Depends(get_order_repo),
    _: None = Depends(require_driver),
) -> list[OrderResponse]:
    return [_to_response(o) for o in order_use_cases.list_orders(order_repo)]


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: str,
    order_repo: OrderRepository = Depends(get_order_repo),
    _: None = Depends(require_driver),
) -> OrderResponse:
    return _to_response(order_use_cases.get_order(order_id, order_repo))


@router.post("", response_model=OrderResponse, status_code=201)
def create_order(
    body: CreateOrderRequest,
    order_repo: OrderRepository = Depends(get_order_repo),
    _: None = Depends(require_admin),
) -> OrderResponse:
    order = Order(
        order_id=body.order_id,
        warehouse_id=body.warehouse_id,
        location=Location(lat=body.lat, lng=body.lng),
        weight=body.weight,
        volume=body.volume,
    )
    return _to_response(order_use_cases.create_order(order, order_repo))


@router.put("/{order_id}", response_model=OrderResponse)
def update_order(
    order_id: str,
    body: UpdateOrderRequest,
    order_repo: OrderRepository = Depends(get_order_repo),
    _: None = Depends(require_admin),
) -> OrderResponse:
    order = Order(
        order_id=order_id,
        warehouse_id=body.warehouse_id,
        location=Location(lat=body.lat, lng=body.lng),
        weight=body.weight,
        volume=body.volume,
        status=OrderStatus(body.status),
    )
    return _to_response(order_use_cases.update_order(order_id, order, order_repo))


@router.delete("/{order_id}", status_code=204)
def delete_order(
    order_id: str,
    order_repo: OrderRepository = Depends(get_order_repo),
    _: None = Depends(require_admin),
) -> None:
    order_use_cases.delete_order(order_id, order_repo)
