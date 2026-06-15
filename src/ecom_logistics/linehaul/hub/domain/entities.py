from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
from uuid import UUID
from ecom_logistics.shared.value_objects import Address
from ecom_logistics.shared.exceptions import DomainValidationError
from ecom_logistics.shared.validators import _check_not_empty, _check_lat, _check_lng


class HubType(IntEnum):
    SORTING_CENTER = 1
    LOCAL_HUB = 2


class HubStatus(IntEnum):
    ACTIVE = 1
    INACTIVE = 0


@dataclass
class Hub:
    id: UUID
    name: str
    type: HubType
    address: Address
    status: HubStatus = HubStatus.ACTIVE
    deleted_at: datetime | None = None

    def __post_init__(self):
        eid = str(self.id)
        errors = [
            e for e in [
                _check_not_empty(eid, "name", self.name),
                _check_not_empty(eid, "address.text", self.address.text),
                _check_lat(eid, "address.location.lat", self.address.location.lat),
                _check_lng(eid, "address.location.lng", self.address.location.lng),
            ] if e is not None
        ]
        if errors:
            raise DomainValidationError(errors)