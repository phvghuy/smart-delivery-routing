from supabase import Client

from smart_delivery_routing.domain.models import Vehicle
from smart_delivery_routing.domain.repositories import VehicleRepository


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
        return [self._to_model(row) for row in response.data]

    def get_vehicle_by_id(self, vehicle_id: str) -> Vehicle | None:
        response = (
            self._client.table("vehicles")
            .select("*")
            .eq("vehicle_id", vehicle_id)
            .maybe_single()
            .execute()
        )
        if response is None or response.data is None:
            return None
        return self._to_model(response.data)

    def create_vehicle(self, vehicle: Vehicle) -> Vehicle:
        row = {
            "vehicle_id":           vehicle.vehicle_id,
            "current_warehouse_id": vehicle.current_warehouse_id,
            "capacity_weight":      vehicle.max_weight,
            "capacity_volume":      vehicle.max_volume,
        }
        response = self._client.table("vehicles").insert(row).execute()
        return self._to_model(response.data[0])

    def update_vehicle(self, vehicle: Vehicle) -> Vehicle:
        patch = {
            "current_warehouse_id": vehicle.current_warehouse_id,
            "capacity_weight":      vehicle.max_weight,
            "capacity_volume":      vehicle.max_volume,
        }
        response = (
            self._client.table("vehicles")
            .update(patch)
            .eq("vehicle_id", vehicle.vehicle_id)
            .execute()
        )
        return self._to_model(response.data[0])

    def delete_vehicle(self, vehicle_id: str) -> None:
        self._client.table("vehicles").delete().eq("vehicle_id", vehicle_id).execute()

    @staticmethod
    def _to_model(row: dict) -> Vehicle:
        return Vehicle(
            vehicle_id=row["vehicle_id"],
            current_warehouse_id=row["current_warehouse_id"],
            max_weight=row["capacity_weight"],
            max_volume=row["capacity_volume"],
        )
