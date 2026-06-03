from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from .models import ServiceLevel, ShippingRequestStatus


@dataclass(frozen=True)
class ShippingRequestQuery:
    page_size: int = 20
    statuses: list[ShippingRequestStatus] | None = None
    service_types: list[ServiceLevel] | None = None
    # keyset cursor — cả hai phải được set cùng nhau hoặc cùng None
    cursor_created_at: datetime | None = None
    cursor_id: UUID | None = None