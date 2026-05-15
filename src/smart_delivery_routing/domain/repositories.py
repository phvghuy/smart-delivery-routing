from abc import ABC, abstractmethod

from .models import Order, Vehicle, Warehouse


class OrderRepository(ABC):
    @abstractmethod
    def save_orders(self, orders: list[Order]) -> None: ...

    @abstractmethod
    def get_orders(self) -> list[Order]: ...

    @abstractmethod
    def get_pending_orders(self) -> list[Order]: ...

    @abstractmethod
    def mark_assigned(self, order_ids: list[str]) -> None: ...


class VehicleRepository(ABC):
    @abstractmethod
    def save_vehicles(self, vehicles: list[Vehicle]) -> None: ...

    @abstractmethod
    def get_vehicles(self) -> list[Vehicle]: ...

    @abstractmethod
    def update_warehouse(self, vehicle_id: str, warehouse_id: str) -> None: ...


class WarehouseRepository(ABC):
    @abstractmethod
    def save_warehouses(self, warehouses: list[Warehouse]) -> None: ...

    @abstractmethod
    def get_warehouses(self) -> list[Warehouse]: ...
