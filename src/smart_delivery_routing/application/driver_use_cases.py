import time
from dataclasses import dataclass
from uuid import UUID

from smart_delivery_routing.domain.delivery import (
    Driver,
    DriverQuery,
    DriverRepository,
    DriverStatus,
    validate_driver,
)
from smart_delivery_routing.domain.shared import ValidationError


@dataclass(frozen=True)
class PagedDrivers:
    items: list[Driver]
    total: int
    page: int
    size: int

    @property
    def pages(self) -> int:
        return max(1, -(-self.total // self.size))


# --- Domain exceptions ---

@dataclass(frozen=True)
class ValidationFailed(Exception):
    errors: list[ValidationError]

    def __str__(self) -> str:
        return "; ".join(f"{e.field}: {e.reason}" for e in self.errors)


@dataclass(frozen=True)
class DriverNotFound(Exception):
    driver_id: UUID

    def __str__(self) -> str:
        return f"Driver '{self.driver_id}' not found."


@dataclass(frozen=True)
class DriverNotDeletable(Exception):
    driver_id: UUID
    status: DriverStatus

    def __str__(self) -> str:
        return f"Driver '{self.driver_id}' cannot be deleted while in status '{self.status.name}'."


# --- Use cases ---

_NON_DELETABLE_STATUSES = {DriverStatus.DELIVERING}


def list_drivers(query: DriverQuery, repo: DriverRepository) -> PagedDrivers:
    start = time.perf_counter()
    items, total = repo.list(query)
    print(f"repo.list took {(time.perf_counter() - start) * 1000:.2f} ms")
    return PagedDrivers(items=items, total=total, page=query.page, size=query.page_size)


def get_driver(driver_id: UUID, repo: DriverRepository) -> Driver:
    driver = repo.get_by_id(driver_id)
    if driver is None:
        raise DriverNotFound(driver_id=driver_id)
    return driver


def create_driver(driver: Driver, repo: DriverRepository) -> Driver:
    errors = validate_driver(driver)
    if errors:
        raise ValidationFailed(errors=errors)
    return repo.create(driver)


def update_driver(driver_id: UUID, updated: Driver, repo: DriverRepository) -> Driver:
    errors = validate_driver(updated)
    if errors:
        raise ValidationFailed(errors=errors)
    if repo.get_by_id(driver_id) is None:
        raise DriverNotFound(driver_id=driver_id)
    return repo.update(updated)


def delete_driver(driver_id: UUID, repo: DriverRepository) -> None:
    driver = repo.get_by_id(driver_id)
    if driver is None:
        raise DriverNotFound(driver_id=driver_id)
    if driver.status in _NON_DELETABLE_STATUSES:
        raise DriverNotDeletable(driver_id=driver_id, status=driver.status)
    repo.delete(driver_id)