from fastapi import APIRouter, Depends

from smart_delivery_routing.application import warehouse_use_cases
from smart_delivery_routing.domain.models import Location, Warehouse
from smart_delivery_routing.domain.repositories import OrderRepository, WarehouseRepository
from ..dependencies import get_order_repo, get_warehouse_repo, require_admin, require_driver
from ..schemas import CreateWarehouseRequest, UpdateWarehouseRequest, WarehouseResponse

router = APIRouter(prefix="/warehouses", tags=["warehouses"])


def _to_response(warehouse: Warehouse) -> WarehouseResponse:
    return WarehouseResponse(
        warehouse_id=warehouse.warehouse_id,
        name=warehouse.name,
        lat=warehouse.location.lat,
        lng=warehouse.location.lng,
    )


@router.get("", response_model=list[WarehouseResponse])
def list_warehouses(
    warehouse_repo: WarehouseRepository = Depends(get_warehouse_repo),
    _: None = Depends(require_driver),
) -> list[WarehouseResponse]:
    return [_to_response(w) for w in warehouse_use_cases.list_warehouses(warehouse_repo)]


@router.get("/{warehouse_id}", response_model=WarehouseResponse)
def get_warehouse(
    warehouse_id: str,
    warehouse_repo: WarehouseRepository = Depends(get_warehouse_repo),
    _: None = Depends(require_driver),
) -> WarehouseResponse:
    return _to_response(warehouse_use_cases.get_warehouse(warehouse_id, warehouse_repo))


@router.post("", response_model=WarehouseResponse, status_code=201)
def create_warehouse(
    body: CreateWarehouseRequest,
    warehouse_repo: WarehouseRepository = Depends(get_warehouse_repo),
    _: None = Depends(require_admin),
) -> WarehouseResponse:
    warehouse = Warehouse(
        warehouse_id=body.warehouse_id,
        name=body.name,
        location=Location(lat=body.lat, lng=body.lng),
    )
    return _to_response(warehouse_use_cases.create_warehouse(warehouse, warehouse_repo))


@router.put("/{warehouse_id}", response_model=WarehouseResponse)
def update_warehouse(
    warehouse_id: str,
    body: UpdateWarehouseRequest,
    warehouse_repo: WarehouseRepository = Depends(get_warehouse_repo),
    _: None = Depends(require_admin),
) -> WarehouseResponse:
    warehouse = Warehouse(
        warehouse_id=warehouse_id,
        name=body.name,
        location=Location(lat=body.lat, lng=body.lng),
    )
    return _to_response(warehouse_use_cases.update_warehouse(warehouse_id, warehouse, warehouse_repo))


@router.delete("/{warehouse_id}", status_code=204)
def delete_warehouse(
    warehouse_id: str,
    warehouse_repo: WarehouseRepository = Depends(get_warehouse_repo),
    order_repo: OrderRepository = Depends(get_order_repo),
    _: None = Depends(require_admin),
) -> None:
    warehouse_use_cases.delete_warehouse(warehouse_id, warehouse_repo, order_repo)
