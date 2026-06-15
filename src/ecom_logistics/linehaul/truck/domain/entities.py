from enum import IntEnum
from dataclasses import dataclass
from uuid import UUID
from datetime import datetime
from ecom_logistics.shared import Capacity
from ecom_logistics.shared.exceptions import DomainValidationError
from ecom_logistics.shared.validators import _check_not_empty, _check_positive


class TruckStatus(IntEnum):
    AVAILABLE = 1
    IN_TRANSIT = 2
    INACTIVE = 0


@dataclass
class Truck:
    id: UUID
    plate_number: str
    capacity: Capacity
    status: TruckStatus = TruckStatus.AVAILABLE
    deleted_at: datetime | None = None

    def __post_init__(self):
        eid = str(self.id)
        errors = [
            e for e in [
                _check_not_empty(eid, "plate_number", self.plate_number),
                _check_positive(eid, "capacity.max_weight", self.capacity.max_weight),
                _check_positive(eid, "capacity.max_volume", self.capacity.max_volume),
            ] if e is not None
        ]
        if errors:
            raise DomainValidationError(errors)