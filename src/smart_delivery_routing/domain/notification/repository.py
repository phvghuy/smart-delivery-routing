from abc import ABC, abstractmethod

from .models import Notification


class NotificationRepository(ABC):
    @abstractmethod
    def create(self, notification: Notification) -> Notification: ...

    @abstractmethod
    def get_by_driver(self, driver_id: str) -> list[Notification]: ...

    @abstractmethod
    def mark_as_read(self, notification_id: str, driver_id: str) -> None: ...
