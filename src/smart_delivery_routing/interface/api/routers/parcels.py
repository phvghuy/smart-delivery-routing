from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from smart_delivery_routing.application import parcel_use_cases
from smart_delivery_routing.application.parcel_use_cases import ParcelNotFound
from smart_delivery_routing.domain.linehaul import Parcel, ParcelQuery, ParcelRepository, ParcelStatus
from ..dependencies import get_parcel_repo, require_admin
from ..schemas import CursorPagedParcelResponse, ParcelResponse

router = APIRouter(prefix="/parcels", tags=["parcels"])


def _to_response(p: Parcel) -> ParcelResponse:
    return ParcelResponse(
        id=str(p.id),
        shipping_request_id=str(p.shipping_request_id),
        tracking_number=p.tracking_number,
        origin_hub_id=str(p.origin_hub_id),
        origin_hub_name=p.origin_hub_name,
        destination_hub_id=str(p.destination_hub_id),
        destination_hub_name=p.destination_hub_name,
        current_hub_id=str(p.current_hub_id) if p.current_hub_id else None,
        current_hub_name=p.current_hub_name,
        weight=p.load.weight,
        volume=p.load.volume,
        status=p.status.value,
        created_at=p.created_at.isoformat(),
        updated_at=p.updated_at.isoformat(),
    )


@router.get("", response_model=CursorPagedParcelResponse)
def list_parcels(
    cursor: str | None = Query(None, description="Opaque cursor từ response trước"),
    size: int = Query(20, ge=1, le=100),
    statuses: list[int] | None = Query(None, description="Lọc theo status: ?statuses=1&statuses=2"),
    repo: ParcelRepository = Depends(get_parcel_repo),
    _: None = Depends(require_admin),
) -> CursorPagedParcelResponse:
    query = ParcelQuery(
        page_size=size,
        statuses=[ParcelStatus(s) for s in statuses] if statuses else None,
    )
    page = parcel_use_cases.list_parcels(query, repo, cursor=cursor)
    return CursorPagedParcelResponse(
        items=[_to_response(p) for p in page.items],
        next_cursor=page.next_cursor,
    )


@router.get("/{parcel_id}", response_model=ParcelResponse)
def get_parcel(
    parcel_id: str,
    repo: ParcelRepository = Depends(get_parcel_repo),
    _: None = Depends(require_admin),
) -> ParcelResponse:
    try:
        parcel = parcel_use_cases.get_parcel(UUID(parcel_id), repo)
    except ParcelNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    return _to_response(parcel)