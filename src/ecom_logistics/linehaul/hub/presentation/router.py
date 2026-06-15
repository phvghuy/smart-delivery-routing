from uuid import UUID

from fastapi import APIRouter, Depends, Query

from ecom_logistics.app.dependencies import get_hub_repo, get_hub_query_repo
from ecom_logistics.auth.presentation.dependencies import require_admin
from ecom_logistics.linehaul.hub.application import (
    CreateHubUseCase,
    UpdateHubUseCase,
    DeleteHubUseCase,
    GetHubUseCase,
    HubQuery,
    ListHubsUseCase,
)
from ecom_logistics.linehaul.hub.domain import Hub, HubStatus, HubType
from ecom_logistics.linehaul.hub.presentation.schemas import (
    CreateHubRequest,
    HubResponse,
    PaginatedHubResponse,
    UpdateHubRequest,
)

router = APIRouter(prefix="/hubs", tags=["hubs"])


def _to_response(hub: Hub) -> HubResponse:
    return HubResponse(
        id=str(hub.id),
        name=hub.name,
        type=hub.type.value,
        address_text=hub.address.text,
        lat=hub.address.location.lat,
        lng=hub.address.location.lng,
        status=hub.status.value,
        deleted_at=hub.deleted_at.isoformat() if hub.deleted_at else None,
    )


@router.get("", response_model=PaginatedHubResponse)
def list_hubs(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None),
    statuses: list[int] | None = Query(None),
    types: list[int] | None = Query(None),
    include_deleted: bool = Query(False),
    repo=Depends(get_hub_query_repo),
    _: None = Depends(require_admin),
) -> PaginatedHubResponse:
    query = HubQuery(
        page=page,
        page_size=size,
        search=search,
        statuses=[HubStatus(s) for s in statuses] if statuses else None,
        types=[HubType(t) for t in types] if types else None,
        include_deleted=include_deleted,
    )
    result = ListHubsUseCase(repo).execute(query)
    return PaginatedHubResponse(
        items=[_to_response(h) for h in result.items],
        total=result.total,
        page=result.page,
        size=result.size,
        pages=result.pages,
    )


@router.get("/{hub_id}", response_model=HubResponse)
def get_hub(
    hub_id: UUID,
    repo=Depends(get_hub_query_repo),
    _: None = Depends(require_admin),
) -> HubResponse:
    hub = GetHubUseCase(repo).execute(hub_id)
    return _to_response(hub)


@router.post("", response_model=HubResponse, status_code=201)
def create_hub(
    body: CreateHubRequest,
    repo=Depends(get_hub_repo),
    _: None = Depends(require_admin),
) -> HubResponse:
    hub = CreateHubUseCase(repo).execute(
        name=body.name,
        type=HubType(body.type),
        address_text=body.address_text,
        lat=body.lat,
        lng=body.lng,
    )
    return _to_response(hub)


@router.put("/{hub_id}", response_model=HubResponse)
def update_hub(
    hub_id: UUID,
    body: UpdateHubRequest,
    repo=Depends(get_hub_repo),
    _: None = Depends(require_admin),
) -> HubResponse:
    hub = UpdateHubUseCase(repo).execute(
        id=hub_id,
        name=body.name,
        type=HubType(body.type),
        address_text=body.address_text,
        lat=body.lat,
        lng=body.lng,
        status=HubStatus(body.status),
    )
    return _to_response(hub)


@router.delete("/{hub_id}", status_code=204)
def delete_hub(
    hub_id: UUID,
    repo=Depends(get_hub_repo),
    _: None = Depends(require_admin),
) -> None:
    DeleteHubUseCase(repo).execute(hub_id)
