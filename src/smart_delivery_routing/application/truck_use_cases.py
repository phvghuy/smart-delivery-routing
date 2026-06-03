from dataclasses import dataclass
from uuid import UUID

from smart_delivery_routing.domain.linehaul import Truck, TruckQuery, TruckRepository, validate_truck
from smart_delivery_routing.domain.shared import ValidationError


@dataclass(frozen=True)
class PagedTrucks:
    items: list[Truck]
    total: int
    page: int
    size: int

    @property
    def pages(self) -> int:
        return max(1, -(-self.total // self.size))


@dataclass(frozen=True)
class ValidationFailed(Exception):
    errors: list[ValidationError]

    def __str__(self) -> str:
        return "; ".join(f"{e.field}: {e.reason}" for e in self.errors)


@dataclass(frozen=True)
class TruckNotFound(Exception):
    truck_id: UUID

    def __str__(self) -> str:
        return f"Truck '{self.truck_id}' not found."


def list_trucks(query: TruckQuery, repo: TruckRepository) -> PagedTrucks:
    items, total = repo.list(query)
    return PagedTrucks(items=items, total=total, page=query.page, size=query.page_size)


def get_truck(truck_id: UUID, repo: TruckRepository) -> Truck:
    truck = repo.get_by_id(truck_id)
    if truck is None:
        raise TruckNotFound(truck_id=truck_id)
    return truck


def create_truck(truck: Truck, repo: TruckRepository) -> Truck:
    errors = validate_truck(truck)
    if errors:
        raise ValidationFailed(errors=errors)
    return repo.create(truck)


def update_truck(truck_id: UUID, updated: Truck, repo: TruckRepository) -> Truck:
    errors = validate_truck(updated)
    if errors:
        raise ValidationFailed(errors=errors)
    if repo.get_by_id(truck_id) is None:
        raise TruckNotFound(truck_id=truck_id)
    return repo.update(updated)


def delete_truck(truck_id: UUID, repo: TruckRepository) -> None:
    if repo.get_by_id(truck_id) is None:
        raise TruckNotFound(truck_id=truck_id)
    repo.delete(truck_id)