from supabase import Client

from smart_delivery_routing.domain.models import Vehicle
from smart_delivery_routing.domain.ports import VehicleRepository


class SupabaseVehicleRepository(VehicleRepository):
    def __init__(self, client: Client) -> None:
        self._client = client

    def save_vehicles(self, vehicles: list[Vehicle]) -> None:
        rows = [
            {
                "vehicle_id":           v.vehicle_id,
                "current_warehouse_id": v.current_warehouse_id,
                "capacity_weight":      v.max_weight,
                "capacity_volume":      v.max_volume,
            }
            for v in vehicles
        ]
        self._client.table("vehicles").upsert(rows).execute()

    def update_warehouse(self, vehicle_id: str, warehouse_id: str) -> None:
        self._client.table("vehicles").update({"current_warehouse_id": warehouse_id}).eq("vehicle_id", vehicle_id).execute()

    def get_vehicles(self) -> list[Vehicle]:
        response = self._client.table("vehicles").select("*").execute()
        return [
            Vehicle(
                vehicle_id=row["vehicle_id"],
                current_warehouse_id=row["current_warehouse_id"],
                max_weight=row["capacity_weight"],
                max_volume=row["capacity_volume"],
            )
            for row in response.data
        ]
