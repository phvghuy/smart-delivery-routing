from supabase import Client

from smart_delivery_routing.domain.notification import Notification, NotificationRepository


class SupabaseNotificationRepository(NotificationRepository):
    def __init__(self, client: Client) -> None:
        self._client = client

    def create(self, notification: Notification) -> Notification:
        row = {
            "driver_id": notification.driver_id,
            "title": notification.title,
            "body": notification.body,
            "data": notification.data,
        }
        response = self._client.table("notifications").insert(row).execute()
        return self._to_model(response.data[0])

    def get_by_driver(self, driver_id: str) -> list[Notification]:
        response = (
            self._client.table("notifications")
            .select("*")
            .eq("driver_id", driver_id)
            .order("created_at", desc=True)
            .execute()
        )
        return [self._to_model(row) for row in response.data]

    def mark_as_read(self, notification_id: str, driver_id: str) -> None:
        self._client.table("notifications").update({"is_read": True}).eq("id", notification_id).eq("driver_id", driver_id).execute()

    @staticmethod
    def _to_model(row: dict) -> Notification:
        return Notification(
            notification_id=row["id"],
            driver_id=row["driver_id"],
            title=row["title"],
            body=row["body"],
            data=row.get("data") or {},
            is_read=row["is_read"],
            created_at=row["created_at"],
        )
