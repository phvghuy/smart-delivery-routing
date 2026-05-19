from supabase import Client

from smart_delivery_routing.domain.models import Location, Route, Stop
from smart_delivery_routing.domain.repositories import RouteRepository


class SupabaseRouteRepository(RouteRepository):
    def __init__(self, client: Client) -> None:
        self._client = client

    def save_routes(self, job_id: str, routes: list[Route]) -> None:
        rows = [
            {
                "job_id": job_id,
                "vehicle_id": r.vehicle_id,
                "total_distance_km": r.total_distance,
                "stops": [{"order_id": s.order_id, "lat": s.location.lat, "lng": s.location.lng} for s in r.stops],
            }
            for r in routes
            if r.stops
        ]
        if rows:
            self._client.table("routes").insert(rows).execute()

    def get_routes_by_job(self, job_id: str) -> list[Route]:
        response = (
            self._client.table("routes")
            .select("*")
            .eq("job_id", job_id)
            .order("vehicle_id")
            .execute()
        )
        return [self._to_model(row) for row in response.data]

    def get_route_by_vehicle(self, job_id: str, vehicle_id: str) -> Route | None:
        response = (
            self._client.table("routes")
            .select("*")
            .eq("job_id", job_id)
            .eq("vehicle_id", vehicle_id)
            .maybe_single()
            .execute()
        )
        if response is None or response.data is None:
            return None
        return self._to_model(response.data)

    @staticmethod
    def _to_model(row: dict) -> Route:
        stops = [
            Stop(order_id=s["order_id"], location=Location(lat=s["lat"], lng=s["lng"]))
            for s in (row.get("stops") or [])
        ]
        return Route(
            vehicle_id=row["vehicle_id"],
            stops=stops,
            total_distance=row["total_distance_km"],
        )
