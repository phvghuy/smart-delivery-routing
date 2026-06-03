from datetime import datetime, timezone
from uuid import UUID

from supabase import Client

from smart_delivery_routing.domain.linehaul import Truck, TruckQuery, TruckRepository, TruckStatus
from smart_delivery_routing.domain.shared import Capacity


class SupabaseTruckRepository(TruckRepository):
    def __init__(self, client: Client) -> None:
        self._client = client

    def create(self, truck: Truck) -> Truck:
        row = self._client.table("trucks").insert(self._to_row(truck)).execute()
        return self._to_model(row.data[0])

    def get_by_id(self, truck_id: UUID) -> Truck | None:
        response = (
            self._client.table("trucks")
            .select("*")
            .eq("id", str(truck_id))
            .maybe_single()
            .execute()
        )
        if response is None or response.data is None:
            return None
        return self._to_model(response.data)

    def list(self, query: TruckQuery) -> tuple[list[Truck], int]:
        from_idx = (query.page - 1) * query.page_size
        to_idx = from_idx + query.page_size - 1

        q = self._client.table("trucks").select("*", count="exact").range(from_idx, to_idx)

        if not query.include_deleted:
            q = q.is_("deleted_at", "null")

        if query.statuses:
            q = q.in_("status", [s.value for s in query.statuses])

        if query.search:
            subjects = [s.strip() for s in query.search.split(",") if s.strip()]
            conditions = ",".join(f"plate_number.ilike.%{s}%" for s in subjects)
            q = q.or_(conditions)

        response = q.execute()
        return [self._to_model(row) for row in response.data], response.count or 0

    def update(self, truck: Truck) -> Truck:
        response = (
            self._client.table("trucks")
            .update(self._to_row(truck))
            .eq("id", str(truck.id))
            .execute()
        )
        return self._to_model(response.data[0])

    def delete(self, truck_id: UUID) -> None:
        self._client.table("trucks").update(
            {"deleted_at": datetime.now(timezone.utc).isoformat()}
        ).eq("id", str(truck_id)).execute()

    @staticmethod
    def _to_row(truck: Truck) -> dict:
        return {
            "id": str(truck.id),
            "plate_number": truck.plate_number,
            "max_weight": truck.capacity.max_weight,
            "max_volume": truck.capacity.max_volume,
            "status": truck.status.value,
        }

    @staticmethod
    def _to_model(row: dict) -> Truck:
        return Truck(
            id=UUID(row["id"]),
            plate_number=row["plate_number"],
            capacity=Capacity(max_weight=row["max_weight"], max_volume=row["max_volume"]),
            status=TruckStatus(row["status"]),
            deleted_at=datetime.fromisoformat(row["deleted_at"]) if row.get("deleted_at") else None,
        )