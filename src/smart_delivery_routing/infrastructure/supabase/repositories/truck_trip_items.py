from datetime import datetime
from uuid import UUID

from supabase import Client

from smart_delivery_routing.domain.linehaul import TruckTripItemRepository
from smart_delivery_routing.domain.linehaul.models import TruckTripItem
from smart_delivery_routing.domain.shared import Load


class SupabaseTruckTripItemRepository(TruckTripItemRepository):
    def __init__(self, client: Client) -> None:
        self._client = client

    def create(self, item: TruckTripItem) -> TruckTripItem:
        row = (
            self._client.table("truck_trip_items")
            .insert(self._to_row(item))
            .execute()
        )
        return self._to_model(row.data[0])

    def get_by_id(self, item_id: UUID) -> TruckTripItem | None:
        response = (
            self._client.table("truck_trip_items")
            .select("*")
            .eq("id", str(item_id))
            .maybe_single()
            .execute()
        )
        if response is None or response.data is None:
            return None
        return self._to_model(response.data)

    def list_by_trip_id(self, trip_id: UUID) -> list[TruckTripItem]:
        response = (
            self._client.table("truck_trip_items")
            .select("*")
            .eq("truck_trip_id", str(trip_id))
            .order("loaded_at", desc=False)
            .execute()
        )
        return [self._to_model(row) for row in response.data]

    def get_used_load_by_trip_id(self, trip_id: UUID) -> Load:
        response = (
            self._client.table("truck_trip_items")
            .select("parcel:parcels(weight, volume)")
            .eq("truck_trip_id", str(trip_id))
            .execute()
        )
        total_weight = sum(row["parcel"]["weight"] for row in response.data if row.get("parcel"))
        total_volume = sum(row["parcel"]["volume"] for row in response.data if row.get("parcel"))
        return Load(weight=total_weight, volume=total_volume)

    def delete(self, item_id: UUID) -> None:
        self._client.table("truck_trip_items").delete().eq("id", str(item_id)).execute()

    @staticmethod
    def _to_row(item: TruckTripItem) -> dict:
        row: dict = {
            "id": str(item.id),
            "truck_trip_id": str(item.truck_trip_id),
            "parcel_id": str(item.parcel_id),
            "loaded_at": item.loaded_at.isoformat(),
        }
        if item.unloaded_at is not None:
            row["unloaded_at"] = item.unloaded_at.isoformat()
        return row

    @staticmethod
    def _to_model(row: dict) -> TruckTripItem:
        return TruckTripItem(
            id=UUID(row["id"]),
            truck_trip_id=UUID(row["truck_trip_id"]),
            parcel_id=UUID(row["parcel_id"]),
            loaded_at=datetime.fromisoformat(row["loaded_at"]),
            unloaded_at=datetime.fromisoformat(row["unloaded_at"]) if row.get("unloaded_at") else None,
        )