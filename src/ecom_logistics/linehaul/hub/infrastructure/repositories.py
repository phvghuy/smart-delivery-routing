from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from postgrest import CountMethod
from supabase import Client
from ecom_logistics.shared import Address, Location
from ecom_logistics.linehaul.hub.domain import Hub, HubRepository, HubStatus, HubType
from ecom_logistics.linehaul.hub.application import HubQuery, HubQueryRepository


def _to_row(hub: Hub) -> dict:
    return {
        "id": str(hub.id),
        "name": hub.name,
        "type": hub.type.value,
        "address_text": hub.address.text,
        "lat": hub.address.location.lat,
        "lng": hub.address.location.lng,
        "status": hub.status.value,
    }


def _to_model(row: Any) -> Hub:
    return Hub(
        id=UUID(row["id"]),
        name=row["name"],
        type=HubType(row["type"]),
        address=Address(
            text=row["address_text"],
            location=Location(lat=float(row["lat"]), lng=float(row["lng"])),
        ),
        status=HubStatus(row["status"]),
        deleted_at=datetime.fromisoformat(row["deleted_at"]) if row.get("deleted_at") else None,
    )


class SupabaseHubRepository(HubRepository):
    def __init__(self, client: Client) -> None:
        self._client = client

    def get_by_id(self, hub_id: UUID) -> Hub | None:
        response = (
            self._client.table("hubs")
            .select("*")
            .eq("id", str(hub_id))
            .maybe_single()
            .execute()
        )
        if response is None or response.data is None:
            return None
        return _to_model(response.data)

    def create(self, hub: Hub) -> Hub:
        row = self._client.table("hubs").insert(_to_row(hub)).execute()
        return _to_model(row.data[0])
    
    
    def update(self, hub: Hub) -> Hub:
        response = (
            self._client.table("hubs")
            .update(_to_row(hub))
            .eq("id", str(hub.id))
            .execute()
        )
        return _to_model(response.data[0])

    def delete(self, hub_id: UUID) -> None:
        self._client.table("hubs").update(
            {"deleted_at": datetime.now(timezone.utc).isoformat()}
        ).eq("id", str(hub_id)).execute()



class SupabaseHubQueryRepository(HubQueryRepository):
    def __init__(self, client: Client) -> None:
        self._client = client

    def get_by_id(self, hub_id: UUID) -> Hub | None:
        response = (
            self._client.table("hubs")
            .select("*")
            .eq("id", str(hub_id))
            .maybe_single()
            .execute()
        )
        if response is None or response.data is None:
            return None
        return _to_model(response.data)
    
    def list(self, query: HubQuery) -> tuple[list[Hub], int]:
        from_idx = (query.page - 1) * query.page_size
        to_idx = from_idx + query.page_size - 1

        q = self._client.table("hubs").select("*", count=CountMethod.exact).range(from_idx, to_idx)
        if not query.include_deleted:
            q = q.is_("deleted_at", "null")

        if query.statuses:
            q = q.in_("status", [s.value for s in query.statuses])

        if query.types:
            q = q.in_("type", [t.value for t in query.types])

        if query.search:
            subjects = [s.strip() for s in query.search.split(",") if s.strip()]
            conditions = ",".join(
                f"name.ilike.%{s}%,address_text.ilike.%{s}%"
                for s in subjects
            )
            q = q.or_(conditions)

        response = q.execute()
        return [_to_model(row) for row in response.data], response.count or 0