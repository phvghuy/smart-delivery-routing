from datetime import datetime
from uuid import UUID

from supabase import Client

from smart_delivery_routing.domain.linehaul import Parcel, ParcelQuery, ParcelRepository, ParcelStatus
from smart_delivery_routing.domain.shared import Load

_JOIN = (
    "*,"
    "origin_hub:hubs!origin_hub_id(id, name),"
    "destination_hub:hubs!destination_hub_id(id, name),"
    "current_hub:hubs!current_hub_id(id, name)"
)


class SupabaseParcelRepository(ParcelRepository):
    def __init__(self, client: Client) -> None:
        self._client = client

    def create(self, parcel: Parcel) -> Parcel:
        self._client.table("parcels").insert({
            "id": str(parcel.id),
            **self._to_row(parcel),
            "created_at": parcel.created_at.isoformat(),
        }).execute()
        return parcel

    def get_by_id(self, parcel_id: UUID) -> Parcel | None:
        response = (
            self._client.table("parcels")
            .select(_JOIN)
            .eq("id", str(parcel_id))
            .maybe_single()
            .execute()
        )
        if response is None or response.data is None:
            return None
        return self._to_model(response.data)

    def list(self, query: ParcelQuery) -> list[Parcel]:
        q = (
            self._client.table("parcels")
            .select(_JOIN)
            .order("created_at", desc=True)
            .order("id", desc=True)
            .limit(query.page_size + 1)
        )

        if query.statuses:
            q = q.in_("status", [s.value for s in query.statuses])

        if query.cursor_created_at is not None:
            cursor_ts = query.cursor_created_at.isoformat()
            cursor_id = str(query.cursor_id)
            q = q.or_(
                f"created_at.lt.{cursor_ts},"
                f"and(created_at.eq.{cursor_ts},id.lt.{cursor_id})"
            )

        response = q.execute()
        return [self._to_model(row) for row in response.data]
    
    def update(self, parcel: Parcel) -> Parcel:
        response = (
            self._client.table("parcels")
            .update(self._to_row(parcel))
            .eq("id", str(parcel.id))
            .execute()
        )
        return self._to_model(response.data[0])

    @staticmethod
    def _to_row(parcel: Parcel) -> dict:
        return {
            "shipping_request_id": str(parcel.shipping_request_id),
            "tracking_number": parcel.tracking_number,
            "origin_hub_id": str(parcel.origin_hub_id),
            "destination_hub_id": str(parcel.destination_hub_id),
            "current_hub_id": str(parcel.current_hub_id) if parcel.current_hub_id else None,
            "weight": parcel.load.weight,
            "volume": parcel.load.volume,
            "status": parcel.status.value,
        }

    @staticmethod
    def _to_model(row: dict) -> Parcel:
        origin_hub = row.get("origin_hub") or {}
        destination_hub = row.get("destination_hub") or {}
        current_hub = row.get("current_hub") or {}
        return Parcel(
            id=UUID(row["id"]),
            shipping_request_id=UUID(row["shipping_request_id"]),
            tracking_number=row["tracking_number"],
            origin_hub_id=UUID(row["origin_hub_id"]),
            destination_hub_id=UUID(row["destination_hub_id"]),
            current_hub_id=UUID(row["current_hub_id"]) if row.get("current_hub_id") else None,
            load=Load(weight=float(row["weight"]), volume=float(row["volume"])),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            status=ParcelStatus(row["status"]),
            origin_hub_name=origin_hub.get("name", ""),
            destination_hub_name=destination_hub.get("name", ""),
            current_hub_name=current_hub.get("name", ""),
        )