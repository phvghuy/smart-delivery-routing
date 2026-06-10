from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from smart_delivery_routing.domain.delivery import DeliveryRouteRepository, RouteStopRepository
from smart_delivery_routing.domain.delivery.models import DeliveryRoute, DeliveryRouteStatus, RouteStop
from ..dependencies import get_current_driver_id, get_delivery_route_repo, get_route_stop_repo, require_admin, require_driver
from ..schemas import DeliveryRouteResponse, RouteStopResponse

router = APIRouter(prefix="/delivery-routes", tags=["delivery-routes"])


def _route_to_response(route: DeliveryRoute) -> DeliveryRouteResponse:
    return DeliveryRouteResponse(
        id=str(route.id),
        driver_id=str(route.driver_id),
        driver_name=route.driver_name,
        hub_id=str(route.hub_id),
        hub_name=route.hub_name,
        hub_lat=route.hub_lat,
        hub_lng=route.hub_lng,
        status=route.status.value,
        total_distance_km=route.total_distance_km,
        created_at=route.created_at.isoformat(),
    )


def _stop_to_response(stop: RouteStop) -> RouteStopResponse:
    return RouteStopResponse(
        id=str(stop.id),
        route_id=str(stop.route_id),
        parcel_id=str(stop.parcel_id),
        tracking_number=stop.tracking_number,
        status=stop.status.value,
        sequence=stop.sequence,
        lat=stop.location.lat,
        lng=stop.location.lng,
        failed_reason=stop.failed_reason.value if stop.failed_reason else None,
        completed_at=stop.completed_at.isoformat() if stop.completed_at else None,
    )


@router.get("", response_model=list[DeliveryRouteResponse])
def list_delivery_routes(
    date: str | None = Query(None, description="Filter by date (YYYY-MM-DD)"),
    status: int | None = Query(None, description="Filter by status"),
    route_repo: DeliveryRouteRepository = Depends(get_delivery_route_repo),
    _: None = Depends(require_admin),
) -> list[DeliveryRouteResponse]:
    status_enum = DeliveryRouteStatus(status) if status is not None else None
    routes = route_repo.list_all(date=date, status=status_enum)
    return [_route_to_response(r) for r in routes]


# /me must be defined before /{id} so FastAPI matches it as a literal path
@router.get("/me", response_model=DeliveryRouteResponse | None)
def get_my_route(
    driver_id: str = Depends(get_current_driver_id),
    route_repo: DeliveryRouteRepository = Depends(get_delivery_route_repo),
    _: None = Depends(require_driver),
) -> DeliveryRouteResponse | None:
    route = route_repo.get_by_driver_id(UUID(driver_id))
    if route is None or route.status not in (DeliveryRouteStatus.PLANNED, DeliveryRouteStatus.IN_PROGRESS):
        return None
    return _route_to_response(route)


@router.get("/{route_id}", response_model=DeliveryRouteResponse)
def get_delivery_route(
    route_id: str,
    route_repo: DeliveryRouteRepository = Depends(get_delivery_route_repo),
    _: None = Depends(require_admin),
) -> DeliveryRouteResponse:
    route = route_repo.get_by_id(UUID(route_id))
    if route is None:
        raise HTTPException(status_code=404, detail="Route not found")
    return _route_to_response(route)


@router.get("/{route_id}/stops", response_model=list[RouteStopResponse])
def list_route_stops(
    route_id: str,
    stop_repo: RouteStopRepository = Depends(get_route_stop_repo),
    _: None = Depends(require_admin),
) -> list[RouteStopResponse]:
    stops = stop_repo.list_by_route_id(UUID(route_id))
    return [_stop_to_response(s) for s in stops]