from supabase import Client
from smart_delivery_routing.domain.models import Location, Order, OrderStatus
from smart_delivery_routing.domain.ports import OrderRepository

class SupabaseOrderRepository(OrderRepository):
    def __init__(self, client: Client) -> None:
        self._client = client

    def save_orders(self, orders: list[Order]) -> None:
        rows = [
            {
                "order_id":     o.order_id,
                "warehouse_id": o.warehouse_id,
                "dest_lat":     o.location.lat,
                "dest_lng":     o.location.lng,
                "weight":       o.weight,
                "volume":       o.volume,
                "status":       o.status.value,
            }
            for o in orders
        ]
        self._client.table("orders").upsert(rows).execute()

    def mark_assigned(self, order_ids: list[str]) -> None:
        if not order_ids:
            return
        self._client.table("orders").update({"status": OrderStatus.ASSIGNED.value}).in_("order_id", order_ids).execute()

    def get_pending_orders(self) -> list[Order]:
        response = (
            self._client.table("orders")
            .select("*")
            .eq("status", OrderStatus.PENDING.value)
            .execute()
        )
        return [
            Order(
                order_id=row["order_id"],
                warehouse_id=row["warehouse_id"],
                location=Location(lat=row["dest_lat"], lng=row["dest_lng"]),
                weight=row["weight"],
                volume=row["volume"],
            )
            for row in response.data
        ]