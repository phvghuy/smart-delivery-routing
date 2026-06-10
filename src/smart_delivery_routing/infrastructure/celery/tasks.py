from datetime import datetime
from zoneinfo import ZoneInfo

from smart_delivery_routing.application.delivery_route_use_cases import create_delivery_routes
from smart_delivery_routing.config import OSRM_URL
from smart_delivery_routing.infrastructure.celery import celery_app
from smart_delivery_routing.infrastructure.fcm_notification_service import FCMNotificationService
from smart_delivery_routing.infrastructure.osrm.distance import OSRMDistanceCalculator
from smart_delivery_routing.infrastructure.supabase.client import get_supabase_service_client
from smart_delivery_routing.infrastructure.supabase.repositories.delivery_routes import (
    SupabaseDeliveryRouteRepository, SupabaseRouteStopRepository,
)
from smart_delivery_routing.infrastructure.supabase.repositories.drivers import SupabaseDriverRepository
from smart_delivery_routing.infrastructure.supabase.repositories.notifications import SupabaseNotificationRepository
from smart_delivery_routing.infrastructure.supabase.repositories.parcels import SupabaseParcelRepository
from smart_delivery_routing.infrastructure.supabase.repositories.shipping_requests import SupabaseShippingRequestRepository

_VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")
_distance_calculator = OSRMDistanceCalculator(base_url=OSRM_URL)


@celery_app.task(name="create_delivery_routes")
def run_create_delivery_routes() -> None:
    now_vn = datetime.now(_VN_TZ)
    if not (8 <= now_vn.hour < 18):
        return

    client = get_supabase_service_client()

    parcel_repo = SupabaseParcelRepository(client)
    driver_repo = SupabaseDriverRepository(client)
    shipping_request_repo = SupabaseShippingRequestRepository(client)
    route_repo = SupabaseDeliveryRouteRepository(client)
    stop_repo = SupabaseRouteStopRepository(client)
    notification_service = FCMNotificationService(SupabaseNotificationRepository(client))

    routes = create_delivery_routes(
        parcel_repo=parcel_repo,
        driver_repo=driver_repo,
        shipping_request_repo=shipping_request_repo,
        route_repo=route_repo,
        stop_repo=stop_repo,
        distance_calculator=_distance_calculator,
    )

    for route in routes:
        driver = driver_repo.get_by_id(route.driver_id)
        if driver is None or not driver.fcm_token:
            continue
        stops = stop_repo.list_by_route_id(route.id)
        notification_service.send_route_notification(
            driver_id=str(route.driver_id),
            fcm_token=driver.fcm_token,
            vehicle_id=str(route.id),
            stops_count=len(stops),
            distance_km=route.total_distance_km,
            job_id=str(route.id),
        )