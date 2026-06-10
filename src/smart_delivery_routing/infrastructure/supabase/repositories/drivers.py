from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from supabase import Client

from smart_delivery_routing.domain.delivery import Driver, DriverProfile, DriverQuery, DriverRepository, DriverStatus
from smart_delivery_routing.domain.shared import Capacity


class SupabaseDriverRepository(DriverRepository):
    def __init__(self, client: Client) -> None:
        self._client = client

    def create(self, driver: Driver) -> Driver:
        row = self._client.table("drivers").insert(self._to_row(driver)).execute()
        return self._to_model(row.data[0])

    def get_by_id(self, driver_id: UUID) -> Driver | None:
        response = (
            self._client.table("drivers")
            .select("*, hubs(id, name)")
            .eq("id", str(driver_id))
            .maybe_single()
            .execute()
        )
        if response is None or response.data is None:
            return None
        return self._to_model(response.data)

    def list(self, query: DriverQuery) -> tuple[list[Driver], int]:
        from_idx = (query.page - 1) * query.page_size
        to_idx = from_idx + query.page_size - 1

        q = self._client.table("drivers").select("*, hubs(id, name)", count="exact").range(from_idx, to_idx)
        if not query.include_deleted:
            q = q.is_("deleted_at", "null")

        if query.statuses:
            q = q.in_("status", [s.value for s in query.statuses])

        if query.search:
            subjects = [s.strip() for s in query.search.split(",") if s.strip()]
            conditions = ",".join(
                f"name.ilike.%{s}%,phone.ilike.%{s}%,plate_number.ilike.%{s}%"
                for s in subjects
            )
            q = q.or_(conditions)

        response = q.execute()
        return [self._to_model(row) for row in response.data], response.count or 0

    def update(self, driver: Driver) -> Driver:
        response = (
            self._client.table("drivers")
            .update(self._to_row(driver))
            .eq("id", str(driver.id))
            .execute()
        )
        return self._to_model(response.data[0])

    def delete(self, driver_id: UUID) -> None:
        self._client.table("drivers").update(
            {"deleted_at": datetime.now(timezone.utc).isoformat()}
        ).eq("id", str(driver_id)).execute()

    def update_fcm_token(self, driver_id: str, fcm_token: str) -> None:
        self._client.table("drivers").update({"fcm_token": fcm_token}).eq("id", driver_id).execute()

    def list_available(self) -> list[Driver]:
        response = (
            self._client.table("drivers")
            .select("*, hubs(id, name)")
            .eq("status", DriverStatus.AVAILABLE.value)
            .is_("deleted_at", "null")
            .execute()
        )
        return [self._to_model(row) for row in response.data]

    @staticmethod
    def _to_row(driver: Driver) -> dict:
        return {
            "id": str(driver.id),
            "name": driver.profile.name,
            "phone": driver.profile.phone,
            "plate_number": driver.profile.plate_number,
            "current_hub_id": str(driver.current_hub_id),
            "max_weight": driver.capacity.max_weight,
            "max_volume": driver.capacity.max_volume,
            "status": driver.status.value,
            "fcm_token": driver.fcm_token,
        }

    @staticmethod
    def _to_model(row: dict) -> Driver:
        hub = row.get("hubs") or {}
        return Driver(
            id=UUID(row["id"]),
            profile=DriverProfile(
                name=row["name"],
                phone=row["phone"],
                plate_number=row["plate_number"],
            ),
            current_hub_id=UUID(row["current_hub_id"]),
            capacity=Capacity(max_weight=row["max_weight"], max_volume=row["max_volume"]),
            status=DriverStatus(row["status"]),
            fcm_token=row.get("fcm_token") or "",
            deleted_at=datetime.fromisoformat(row["deleted_at"]) if row.get("deleted_at") else None,
            hub_name=hub.get("name", ""),
        )
