from dataclasses import dataclass

from .models import DriverStatus


@dataclass(frozen=True)
class DriverQuery:
    page: int = 1
    page_size: int = 20
    search: str | None = None
    statuses: list[DriverStatus] | None = None
    include_deleted: bool = False
