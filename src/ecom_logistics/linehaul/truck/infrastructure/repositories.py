from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from supabase import Client

from ecom_logistics.linehaul.truck.domain import Truck, TruckRepository, TruckStatus
from ecom_logistics.shared import Capacity


def _to_row(truck: Truck) -> dict:
    return {
        "id": str(truck.id),
        "plate_number": truck.plate_number,
        "max_weight": truck.capacity.max_weight,
        "max_volume": truck.capacity.max_volume,
        "status": truck.status.value,
    }


def _to_model(row: Any) -> Truck:
    return Truck(
        id=UUID(row["id"]),
        plate_number=row["plate_number"],
        capacity=Capacity(max_weight=row["max_weight"], max_volume=row["max_volume"]),
        status=TruckStatus(row["status"]),
        deleted_at=datetime.fromisoformat(row["deleted_at"]) if row.get("deleted_at") else None,
    )


class SupabaseTruckRepository(TruckRepository):
    def __init__(self, client: Client) -> None:
        self._client = client

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
        return _to_model(response.data)

    def create(self, truck: Truck) -> Truck:
        response = self._client.table("trucks").insert(_to_row(truck)).execute()
        return _to_model(response.data[0])

    def update(self, truck: Truck) -> Truck:
        response = (
            self._client.table("trucks")
            .update(_to_row(truck))
            .eq("id", str(truck.id))
            .execute()
        )
        return _to_model(response.data[0])

    def delete(self, truck_id: UUID) -> None:
        self._client.table("trucks").update(
            {"deleted_at": datetime.now(timezone.utc).isoformat()}
        ).eq("id", str(truck_id)).execute()


