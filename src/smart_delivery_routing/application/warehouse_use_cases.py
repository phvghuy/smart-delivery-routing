from dataclasses import dataclass

from smart_delivery_routing.domain.models import OrderStatus, Warehouse
from smart_delivery_routing.domain.repositories import OrderRepository, WarehouseRepository
from smart_delivery_routing.domain.validators import validate_warehouse_fields

from .routing_use_cases import ValidationFailed


# --- Domain exceptions ---

@dataclass(frozen=True)
class WarehouseNotFound(Exception):
    warehouse_id: str

    def __str__(self) -> str:
        return f"Warehouse '{self.warehouse_id}' not found."


@dataclass(frozen=True)
class WarehouseAlreadyExists(Exception):
    warehouse_id: str

    def __str__(self) -> str:
        return f"Warehouse '{self.warehouse_id}' already exists."


@dataclass(frozen=True)
class WarehouseHasActiveOrders(Exception):
    warehouse_id: str
    count: int

    def __str__(self) -> str:
        return (
            f"Warehouse '{self.warehouse_id}' cannot be deleted: "
            f"{self.count} active order(s) still reference it."
        )


# --- Use cases ---

def list_warehouses(repo: WarehouseRepository) -> list[Warehouse]:
    return repo.get_warehouses()


def get_warehouse(warehouse_id: str, repo: WarehouseRepository) -> Warehouse:
    warehouse = repo.get_warehouse_by_id(warehouse_id)
    if warehouse is None:
        raise WarehouseNotFound(warehouse_id=warehouse_id)
    return warehouse


def create_warehouse(warehouse: Warehouse, repo: WarehouseRepository) -> Warehouse:
    errors = validate_warehouse_fields(warehouse)
    if errors:
        raise ValidationFailed(errors)

    if repo.get_warehouse_by_id(warehouse.warehouse_id) is not None:
        raise WarehouseAlreadyExists(warehouse_id=warehouse.warehouse_id)

    return repo.create_warehouse(warehouse)


def update_warehouse(warehouse_id: str, updated: Warehouse, repo: WarehouseRepository) -> Warehouse:
    errors = validate_warehouse_fields(updated)
    if errors:
        raise ValidationFailed(errors)

    if repo.get_warehouse_by_id(warehouse_id) is None:
        raise WarehouseNotFound(warehouse_id=warehouse_id)

    return repo.update_warehouse(updated)


def delete_warehouse(
    warehouse_id: str,
    warehouse_repo: WarehouseRepository,
    order_repo: OrderRepository,
) -> None:
    if warehouse_repo.get_warehouse_by_id(warehouse_id) is None:
        raise WarehouseNotFound(warehouse_id=warehouse_id)

    active = [
        o for o in order_repo.get_orders()
        if o.warehouse_id == warehouse_id
        and o.status in (OrderStatus.PENDING, OrderStatus.ASSIGNED)
    ]
    if active:
        raise WarehouseHasActiveOrders(warehouse_id=warehouse_id, count=len(active))

    warehouse_repo.delete_warehouse(warehouse_id)
