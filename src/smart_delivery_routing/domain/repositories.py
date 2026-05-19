from abc import ABC, abstractmethod

from .models import Driver, Notification, Order, OrderStatus, Route, Vehicle, Warehouse


class OrderRepository(ABC):
    @abstractmethod
    def save_orders(self, orders: list[Order]) -> None: ...

    @abstractmethod
    def get_orders(self) -> list[Order]: ...

    @abstractmethod
    def get_orders_paginated(
        self,
        page: int,
        size: int,
        status: OrderStatus | None = None,
        warehouse_id: str | None = None,
        search: str | None = None,
    ) -> tuple[list[Order], int]: ...

    @abstractmethod
    def get_order_by_id(self, order_id: str) -> Order | None: ...

    @abstractmethod
    def get_pending_orders(self) -> list[Order]: ...

    @abstractmethod
    def create_order(self, order: Order) -> Order: ...

    @abstractmethod
    def update_order(self, order: Order) -> Order: ...

    @abstractmethod
    def delete_order(self, order_id: str) -> None: ...

    @abstractmethod
    def mark_assigned(self, order_ids: list[str]) -> None: ...

    @abstractmethod
    def update_job_id(self, order_ids: list[str], job_id: str) -> None: ...

    @abstractmethod
    def count_active_in_batch(self, job_id: str) -> int: ...


class VehicleRepository(ABC):
    @abstractmethod
    def save_vehicles(self, vehicles: list[Vehicle]) -> None: ...

    @abstractmethod
    def get_vehicles(self) -> list[Vehicle]: ...

    @abstractmethod
    def get_vehicle_by_id(self, vehicle_id: str) -> Vehicle | None: ...

    @abstractmethod
    def create_vehicle(self, vehicle: Vehicle) -> Vehicle: ...

    @abstractmethod
    def update_vehicle(self, vehicle: Vehicle) -> Vehicle: ...

    @abstractmethod
    def delete_vehicle(self, vehicle_id: str) -> None: ...

    @abstractmethod
    def update_warehouse(self, vehicle_id: str, warehouse_id: str) -> None: ...


class WarehouseRepository(ABC):
    @abstractmethod
    def save_warehouses(self, warehouses: list[Warehouse]) -> None: ...

    @abstractmethod
    def get_warehouses(self) -> list[Warehouse]: ...

    @abstractmethod
    def get_warehouse_by_id(self, warehouse_id: str) -> Warehouse | None: ...

    @abstractmethod
    def create_warehouse(self, warehouse: Warehouse) -> Warehouse: ...

    @abstractmethod
    def update_warehouse(self, warehouse: Warehouse) -> Warehouse: ...

    @abstractmethod
    def delete_warehouse(self, warehouse_id: str) -> None: ...


class RouteRepository(ABC):
    @abstractmethod
    def save_routes(self, job_id: str, routes: list[Route]) -> None: ...

    @abstractmethod
    def get_routes_by_job(self, job_id: str) -> list[Route]: ...

    @abstractmethod
    def get_route_by_vehicle(self, job_id: str, vehicle_id: str) -> Route | None: ...


class DriverRepository(ABC):
    @abstractmethod
    def get_driver_by_id(self, driver_id: str) -> Driver | None: ...

    @abstractmethod
    def get_driver_by_vehicle_id(self, vehicle_id: str) -> Driver | None: ...

    @abstractmethod
    def upsert_driver(self, driver: Driver) -> Driver: ...

    @abstractmethod
    def update_fcm_token(self, driver_id: str, fcm_token: str) -> None: ...


class NotificationRepository(ABC):
    @abstractmethod
    def create_notification(self, notification: Notification) -> Notification: ...

    @abstractmethod
    def get_notifications_by_driver(self, driver_id: str) -> list[Notification]: ...

    @abstractmethod
    def mark_as_read(self, notification_id: str, driver_id: str) -> None: ... 
