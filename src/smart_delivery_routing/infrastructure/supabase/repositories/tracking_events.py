from datetime import datetime
from uuid import UUID

from supabase import Client

from smart_delivery_routing.domain.linehaul import ParcelStatus
from smart_delivery_routing.domain.tracking import TrackingEvent, TrackingLocation, TrackingLocationType
from smart_delivery_routing.domain.tracking.repository import TrackingEventRepository


class SupabaseTrackingEventRepository(TrackingEventRepository):
    def __init__(self, client: Client) -> None:
        self._client = client

    def create(self, event: TrackingEvent) -> TrackingEvent:
        row = self._client.table("tracking_events").insert(self._to_row(event)).execute()
        return self._to_model(row.data[0])

    def list_by_parcel_id(self, parcel_id: UUID) -> list[TrackingEvent]:
        response = (
            self._client.table("tracking_events")
            .select("*")
            .eq("parcel_id", str(parcel_id))
            .order("created_at", desc=False)  # timeline: oldest → newest
            .execute()
        )
        return [self._to_model(row) for row in response.data]

    @staticmethod
    def _to_row(event: TrackingEvent) -> dict:
        row: dict = {
            "id": str(event.id),
            "parcel_id": str(event.parcel_id),
            "status": event.status.value,
            "location_kind": event.location.kind.value,
            "location_name": event.location.name,
            "created_at": event.created_at.isoformat(),
        }
        if event.location.id is not None:
            row["location_id"] = str(event.location.id)
        if event.note is not None:
            row["note"] = event.note
        return row

    @staticmethod
    def _to_model(row: dict) -> TrackingEvent:
        return TrackingEvent(
            id=UUID(row["id"]),
            parcel_id=UUID(row["parcel_id"]),
            status=ParcelStatus(row["status"]),
            location=TrackingLocation(
                kind=TrackingLocationType(row["location_kind"]),
                name=row["location_name"],
                id=UUID(row["location_id"]) if row.get("location_id") else None,
            ),
            created_at=datetime.fromisoformat(row["created_at"]),
            note=row.get("note"),
        )
