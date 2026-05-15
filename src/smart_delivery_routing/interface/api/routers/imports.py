from fastapi import APIRouter, Depends, UploadFile

from smart_delivery_routing.application.data_loader import load_orders_from_bytes, load_vehicles_from_bytes, load_warehouses_from_bytes
from smart_delivery_routing.domain.repositories import OrderRepository, VehicleRepository, WarehouseRepository
from ..dependencies import get_order_repo, get_vehicle_repo, get_warehouse_repo, require_admin

router = APIRouter(tags=["imports"])


@router.post("/import/upload", status_code=201)
async def import_upload(
    orders_file: UploadFile,
    vehicles_file: UploadFile,
    warehouses_file: UploadFile,
    order_repo: OrderRepository = Depends(get_order_repo),
    vehicle_repo: VehicleRepository = Depends(get_vehicle_repo),
    warehouse_repo: WarehouseRepository = Depends(get_warehouse_repo),
    _: None = Depends(require_admin),
) -> dict:
    orders = load_orders_from_bytes(await orders_file.read(), source=orders_file.filename or "orders")
    vehicles = load_vehicles_from_bytes(await vehicles_file.read(), source=vehicles_file.filename or "vehicles")
    warehouses = load_warehouses_from_bytes(await warehouses_file.read(), source=warehouses_file.filename or "warehouses")
    order_repo.save_orders(orders)
    vehicle_repo.save_vehicles(vehicles)
    warehouse_repo.save_warehouses(warehouses)
    return {"imported_orders": len(orders), "imported_vehicles": len(vehicles), "imported_warehouses": len(warehouses)}
