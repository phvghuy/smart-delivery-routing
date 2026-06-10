from datetime import date as date_type, datetime, timedelta
from uuid import UUID

from supabase import Client

from smart_delivery_routing.domain.delivery import DeliveryRouteRepository, RouteStopRepository
from smart_delivery_routing.domain.delivery.models import (
    DeliveryRoute, DeliveryRouteStatus, FailedReason, RouteStop, RouteStopStatus,
)
from smart_delivery_routing.domain.shared.value_objects import Location


class SupabaseDeliveryRouteRepository(DeliveryRouteRepository):
    def __init__(self, client: Client) -> None:
        self._client = client

    def save(self, route: DeliveryRoute) -> DeliveryRoute:
        self._client.table("delivery_routes").insert(self._to_row(route)).execute()
        return route

    def get_by_id(self, route_id: UUID) -> DeliveryRoute | None:
        response = (
            self._client.table("delivery_routes")
            .select("*, drivers(id, name), hubs(id, name, lat, lng)")
            .eq("id", str(route_id))
            .maybe_single()
            .execute()
        )
        if response is None or response.data is None:
            return None
        return self._to_model(response.data)

    def list_all(self, date: str | None = None, status: DeliveryRouteStatus | None = None) -> list[DeliveryRoute]:
        q = (
            self._client.table("delivery_routes")
            .select("*, drivers(id, name), hubs(id, name, lat, lng)")
            .order("created_at", desc=True)
        )
        if date:
            next_day = (date_type.fromisoformat(date) + timedelta(days=1)).isoformat()
            q = q.gte("created_at", f"{date}T00:00:00").lt("created_at", f"{next_day}T00:00:00")
        if status is not None:
            q = q.eq("status", status.value)
        response = q.execute()
        return [self._to_model(row) for row in response.data]

    def get_by_driver_id(self, driver_id: UUID) -> DeliveryRoute | None:
        response = (
            self._client.table("delivery_routes")
            .select("*")
            .eq("driver_id", str(driver_id))
            .order("created_at", desc=True)
            .limit(1)
            .maybe_single()
            .execute()
        )
        if response is None or response.data is None:
            return None
        return self._to_model(response.data)

    def update(self, route: DeliveryRoute) -> DeliveryRoute:
        self._client.table("delivery_routes").update({
            "status": route.status.value,
            "total_distance_km": route.total_distance_km,
        }).eq("id", str(route.id)).execute()
        return route

    @staticmethod
    def _to_row(route: DeliveryRoute) -> dict:
        return {
            "id": str(route.id),
            "driver_id": str(route.driver_id),
            "hub_id": str(route.hub_id),
            "status": route.status.value,
            "total_distance_km": route.total_distance_km,
            "created_at": route.created_at.isoformat(),
        }

    @staticmethod
    def _to_model(row: dict) -> DeliveryRoute:
        driver = row.get("drivers") or {}
        hub = row.get("hubs") or {}
        return DeliveryRoute(
            id=UUID(row["id"]),
            driver_id=UUID(row["driver_id"]),
            hub_id=UUID(row["hub_id"]),
            status=DeliveryRouteStatus(row["status"]),
            total_distance_km=row["total_distance_km"],
            created_at=datetime.fromisoformat(row["created_at"]),
            driver_name=driver.get("name", ""),
            hub_name=hub.get("name", ""),
            hub_lat=float(hub.get("lat") or 0),
            hub_lng=float(hub.get("lng") or 0),
        )


class SupabaseRouteStopRepository(RouteStopRepository):
    def __init__(self, client: Client) -> None:
        self._client = client

    def save(self, stop: RouteStop) -> RouteStop:
        self._client.table("route_stops").insert(self._to_row(stop)).execute()
        return stop

    def list_active_parcel_ids(self) -> list[UUID]:
        response = (
            self._client.table("route_stops")
            .select("parcel_id")
            .eq("status", RouteStopStatus.PENDING.value)
            .execute()
        )
        return [UUID(row["parcel_id"]) for row in response.data]

    def list_by_route_id(self, route_id: UUID) -> list[RouteStop]:
        response = (
            self._client.table("route_stops")
            .select("*, parcels(tracking_number)")
            .eq("route_id", str(route_id))
            .order("sequence")
            .execute()
        )
        return [self._to_model(row) for row in response.data]

    def update(self, stop: RouteStop) -> RouteStop:
        row: dict = {"status": stop.status.value}
        if stop.failed_reason is not None:
            row["failed_reason"] = stop.failed_reason.value
        if stop.completed_at is not None:
            row["completed_at"] = stop.completed_at.isoformat()
        self._client.table("route_stops").update(row).eq("id", str(stop.id)).execute()
        return stop

    @staticmethod
    def _to_row(stop: RouteStop) -> dict:
        row: dict = {
            "id": str(stop.id),
            "route_id": str(stop.route_id),
            "parcel_id": str(stop.parcel_id),
            "status": stop.status.value,
            "sequence": stop.sequence,
            "lat": stop.location.lat,
            "lng": stop.location.lng,
        }
        if stop.failed_reason is not None:
            row["failed_reason"] = stop.failed_reason.value
        if stop.completed_at is not None:
            row["completed_at"] = stop.completed_at.isoformat()
        return row

    @staticmethod
    def _to_model(row: dict) -> RouteStop:
        parcel = row.get("parcels") or {}
        return RouteStop(
            id=UUID(row["id"]),
            route_id=UUID(row["route_id"]),
            parcel_id=UUID(row["parcel_id"]),
            status=RouteStopStatus(row["status"]),
            sequence=row["sequence"],
            location=Location(lat=float(row["lat"]), lng=float(row["lng"])),
            failed_reason=FailedReason(row["failed_reason"]) if row.get("failed_reason") else None,
            completed_at=datetime.fromisoformat(row["completed_at"]) if row.get("completed_at") else None,
            tracking_number=parcel.get("tracking_number", ""),
        )