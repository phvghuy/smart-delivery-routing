from datetime import datetime, timezone
from uuid import UUID

from supabase import Client

from smart_delivery_routing.domain.linehaul import TruckTripQuery, TruckTripRepository
from smart_delivery_routing.domain.linehaul.models import TruckTrip, TruckTripStatus

_JOIN = (
    "*,"
    "truck:trucks(id, plate_number),"
    "origin_hub:hubs!origin_hub_id(id, name),"
    "destination_hub:hubs!destination_hub_id(id, name)"
)


class SupabaseTruckTripRepository(TruckTripRepository):
    def __init__(self, client: Client) -> None:
        self._client = client

    def create(self, trip: TruckTrip) -> TruckTrip:
        row = (
            self._client.table("truck_trips")
            .insert(self._to_row(trip))
            .select(_JOIN)
            .execute()
        )
        return self._to_model(row.data[0])

    def get_by_id(self, trip_id: UUID) -> TruckTrip | None:
        response = (
            self._client.table("truck_trips")
            .select(_JOIN)
            .eq("id", str(trip_id))
            .maybe_single()
            .execute()
        )
        if response is None or response.data is None:
            return None
        return self._to_model(response.data)

    def list(self, query: TruckTripQuery) -> tuple[list[TruckTrip], int]:
        from_idx = (query.page - 1) * query.page_size
        to_idx = from_idx + query.page_size - 1

        q = (
            self._client.table("truck_trips")
            .select(_JOIN, count="exact")
            .order("planned_departure_time", desc=True)
            .range(from_idx, to_idx)
        )

        if not query.include_deleted:
            q = q.is_("deleted_at", "null")

        if query.statuses:
            q = q.in_("status", [s.value for s in query.statuses])

        response = q.execute()
        return [self._to_model(row) for row in response.data], response.count or 0

    def update(self, trip: TruckTrip) -> TruckTrip:
        response = (
            self._client.table("truck_trips")
            .update(self._to_row(trip))
            .eq("id", str(trip.id))
            .select(_JOIN)
            .execute()
        )
        return self._to_model(response.data[0])

    def delete(self, trip_id: UUID) -> None:
        self._client.table("truck_trips").update(
            {"deleted_at": datetime.now(timezone.utc).isoformat()}
        ).eq("id", str(trip_id)).execute()

    @staticmethod
    def _to_row(trip: TruckTrip) -> dict:
        row: dict = {
            "id": str(trip.id),
            "truck_id": str(trip.truck_id),
            "origin_hub_id": str(trip.origin_hub_id),
            "destination_hub_id": str(trip.destination_hub_id),
            "status": trip.status.value,
            "planned_departure_time": trip.planned_departure_time.isoformat(),
            "created_at": trip.created_at.isoformat(),
        }
        if trip.actual_departure_time is not None:
            row["actual_departure_time"] = trip.actual_departure_time.isoformat()
        if trip.actual_arrival_time is not None:
            row["actual_arrival_time"] = trip.actual_arrival_time.isoformat()
        return row

    @staticmethod
    def _to_model(row: dict) -> TruckTrip:
        truck = row.get("truck") or {}
        origin_hub = row.get("origin_hub") or {}
        destination_hub = row.get("destination_hub") or {}
        return TruckTrip(
            id=UUID(row["id"]),
            truck_id=UUID(row["truck_id"]),
            origin_hub_id=UUID(row["origin_hub_id"]),
            destination_hub_id=UUID(row["destination_hub_id"]),
            status=TruckTripStatus(row["status"]),
            planned_departure_time=datetime.fromisoformat(row["planned_departure_time"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            actual_departure_time=datetime.fromisoformat(row["actual_departure_time"]) if row.get("actual_departure_time") else None,
            actual_arrival_time=datetime.fromisoformat(row["actual_arrival_time"]) if row.get("actual_arrival_time") else None,
            deleted_at=datetime.fromisoformat(row["deleted_at"]) if row.get("deleted_at") else None,
            truck_plate_number=truck.get("plate_number", ""),
            origin_hub_name=origin_hub.get("name", ""),
            destination_hub_name=destination_hub.get("name", ""),
        )