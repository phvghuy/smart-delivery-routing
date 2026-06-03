from dataclasses import dataclass


@dataclass
class Notification:
    driver_id: str
    title: str
    body: str
    data: dict
    notification_id: str = ""
    is_read: bool = False
    created_at: str = ""
