from firebase_admin import messaging

from smart_delivery_routing.application.services import NotificationService
from smart_delivery_routing.domain.models import Notification
from smart_delivery_routing.domain.repositories import NotificationRepository
from smart_delivery_routing.infrastructure.firebase import initialize_firebase


class FCMNotificationService(NotificationService):
    def __init__(self, notification_repo: NotificationRepository) -> None:
        self._repo = notification_repo
        initialize_firebase()

    def send_route_notification(
        self,
        driver_id: str,
        fcm_token: str,
        vehicle_id: str,
        stops_count: int,
        distance_km: float,
        job_id: str,
    ) -> None:
        body = f"{stops_count} điểm giao · {distance_km:.1f} km"
        self._repo.create_notification(Notification(
            driver_id=driver_id,
            title="Tuyến giao hàng mới",
            body=body,
            data={"vehicle_id": vehicle_id, "job_id": job_id},
        ))
        try:
            messaging.send(messaging.Message(
                notification=messaging.Notification(title="Tuyến giao hàng mới", body=body),
                data={"vehicle_id": vehicle_id, "job_id": job_id},
                token=fcm_token,
            ))
        except Exception:
            pass
