from abc import ABC, abstractmethod
from uuid import UUID

from .models import ShippingRequest, ShippingRequestStatus
from .queries import ShippingRequestQuery


class ShippingRequestRepository(ABC):
    @abstractmethod
    def create(self, request: ShippingRequest) -> ShippingRequest: ...

    @abstractmethod
    def get_by_id(self, request_id: UUID) -> ShippingRequest | None: ...

    @abstractmethod
    def list(self, query: ShippingRequestQuery) -> list[ShippingRequest]: ...

    @abstractmethod
    def update_status(self, request_id: UUID, status: ShippingRequestStatus) -> None: ...