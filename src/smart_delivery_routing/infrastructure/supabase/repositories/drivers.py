from supabase import Client

from smart_delivery_routing.domain.models import Driver
from smart_delivery_routing.domain.repositories import DriverRepository


class SupabaseDriverRepository(DriverRepository):
    def __init__(self, client: Client) -> None:
        self._client = client

    def get_driver_by_id(self, driver_id: str) -> Driver | None:
        response = (
            self._client.table("drivers")
            .select("*")
            .eq("driver_id", driver_id)
            .maybe_single()
            .execute()
        )
        if response is None or response.data is None:
            return None
        return self._to_model(response.data)

    def get_driver_by_vehicle_id(self, vehicle_id: str) -> Driver | None:
        response = (
            self._client.table("drivers")
            .select("*")
            .eq("vehicle_id", vehicle_id)
            .maybe_single()
            .execute()
        )
        if response is None or response.data is None:
            return None
        return self._to_model(response.data)

    def upsert_driver(self, driver: Driver) -> Driver:
        row = {"driver_id": driver.driver_id, "vehicle_id": driver.vehicle_id, "fcm_token": driver.fcm_token}
        response = self._client.table("drivers").upsert(row).execute()
        return self._to_model(response.data[0])

    def update_fcm_token(self, driver_id: str, fcm_token: str) -> None:
        self._client.table("drivers").upsert({"driver_id": driver_id, "fcm_token": fcm_token}).execute()

    @staticmethod
    def _to_model(row: dict) -> Driver:
        return Driver(
            driver_id=row["driver_id"],
            vehicle_id=row.get("vehicle_id"),
            fcm_token=row.get("fcm_token"),
        )
