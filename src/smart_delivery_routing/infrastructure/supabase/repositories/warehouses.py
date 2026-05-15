from supabase import Client

from smart_delivery_routing.domain.models import Location, Warehouse
from smart_delivery_routing.domain.repositories import WarehouseRepository


class SupabaseWarehouseRepository(WarehouseRepository):
    def __init__(self, client: Client) -> None:
        self._client = client

    def save_warehouses(self, warehouses: list[Warehouse]) -> None:
        rows = [
            {
                "warehouse_id": w.warehouse_id,
                "name":         w.name,
                "lat":          w.location.lat,
                "lng":          w.location.lng,
            }
            for w in warehouses
        ]
        self._client.table("warehouses").upsert(rows).execute()

    def get_warehouses(self) -> list[Warehouse]:
        response = self._client.table("warehouses").select("*").execute()
        return [self._to_model(row) for row in response.data]

    def get_warehouse_by_id(self, warehouse_id: str) -> Warehouse | None:
        response = (
            self._client.table("warehouses")
            .select("*")
            .eq("warehouse_id", warehouse_id)
            .maybe_single()
            .execute()
        )
        if response.data is None:
            return None
        return self._to_model(response.data)

    def create_warehouse(self, warehouse: Warehouse) -> Warehouse:
        row = {
            "warehouse_id": warehouse.warehouse_id,
            "name":         warehouse.name,
            "lat":          warehouse.location.lat,
            "lng":          warehouse.location.lng,
        }
        response = self._client.table("warehouses").insert(row).execute()
        return self._to_model(response.data[0])

    def update_warehouse(self, warehouse: Warehouse) -> Warehouse:
        patch = {
            "name": warehouse.name,
            "lat":  warehouse.location.lat,
            "lng":  warehouse.location.lng,
        }
        response = (
            self._client.table("warehouses")
            .update(patch)
            .eq("warehouse_id", warehouse.warehouse_id)
            .execute()
        )
        return self._to_model(response.data[0])

    def delete_warehouse(self, warehouse_id: str) -> None:
        self._client.table("warehouses").delete().eq("warehouse_id", warehouse_id).execute()

    @staticmethod
    def _to_model(row: dict) -> Warehouse:
        return Warehouse(
            warehouse_id=row["warehouse_id"],
            location=Location(lat=row["lat"], lng=row["lng"]),
            name=row["name"],
        )
