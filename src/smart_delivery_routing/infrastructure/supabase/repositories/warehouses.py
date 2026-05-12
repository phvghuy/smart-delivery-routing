from supabase import Client

from smart_delivery_routing.domain.models import Location, Warehouse
from smart_delivery_routing.domain.ports import WarehouseRepository


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
        return [
            Warehouse(
                warehouse_id=row["warehouse_id"],
                location=Location(lat=row["lat"], lng=row["lng"]),
                name=row["name"],
            )
            for row in response.data
        ]
