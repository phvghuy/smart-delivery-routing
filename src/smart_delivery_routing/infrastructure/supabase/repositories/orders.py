from supabase import Client

from smart_delivery_routing.domain.models import Location, Order, OrderStatus
from smart_delivery_routing.domain.repositories import OrderRepository


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

    def get_orders(self) -> list[Order]:
        response = self._client.table("orders").select("*").order("order_id").execute()
        return [
            Order(
                order_id=row["order_id"],
                warehouse_id=row["warehouse_id"],
                location=Location(lat=row["dest_lat"], lng=row["dest_lng"]),
                weight=row["weight"],
                volume=row["volume"],
                status=OrderStatus(row["status"]),
            )
            for row in response.data
        ]

    def get_order_by_id(self, order_id: str) -> Order | None:
        response = (
            self._client.table("orders")
            .select("*")
            .eq("order_id", order_id)
            .maybe_single()
            .execute()
        )
        if response.data is None:
            return None
        row = response.data
        return Order(
            order_id=row["order_id"],
            warehouse_id=row["warehouse_id"],
            location=Location(lat=row["dest_lat"], lng=row["dest_lng"]),
            weight=row["weight"],
            volume=row["volume"],
            status=OrderStatus(row["status"]),
        )

    def create_order(self, order: Order) -> Order:
        row = {
            "order_id":     order.order_id,
            "warehouse_id": order.warehouse_id,
            "dest_lat":     order.location.lat,
            "dest_lng":     order.location.lng,
            "weight":       order.weight,
            "volume":       order.volume,
            "status":       order.status.value,
        }
        response = self._client.table("orders").insert(row).execute()
        created = response.data[0]
        return Order(
            order_id=created["order_id"],
            warehouse_id=created["warehouse_id"],
            location=Location(lat=created["dest_lat"], lng=created["dest_lng"]),
            weight=created["weight"],
            volume=created["volume"],
            status=OrderStatus(created["status"]),
        )

    def update_order(self, order: Order) -> Order:
        patch = {
            "warehouse_id": order.warehouse_id,
            "dest_lat":     order.location.lat,
            "dest_lng":     order.location.lng,
            "weight":       order.weight,
            "volume":       order.volume,
            "status":       order.status.value,
        }
        response = (
            self._client.table("orders")
            .update(patch)
            .eq("order_id", order.order_id)
            .execute()
        )
        updated = response.data[0]
        return Order(
            order_id=updated["order_id"],
            warehouse_id=updated["warehouse_id"],
            location=Location(lat=updated["dest_lat"], lng=updated["dest_lng"]),
            weight=updated["weight"],
            volume=updated["volume"],
            status=OrderStatus(updated["status"]),
        )

    def delete_order(self, order_id: str) -> None:
        self._client.table("orders").delete().eq("order_id", order_id).execute()

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
