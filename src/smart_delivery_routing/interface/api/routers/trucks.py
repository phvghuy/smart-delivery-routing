from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from smart_delivery_routing.application import truck_use_cases
from smart_delivery_routing.application.truck_use_cases import TruckNotFound, ValidationFailed
from smart_delivery_routing.domain.linehaul import Truck, TruckQuery, TruckRepository, TruckStatus
from smart_delivery_routing.domain.shared import Capacity
from ..dependencies import get_truck_repo, require_admin
from ..schemas import CreateTruckRequest, PaginatedTruckResponse, TruckResponse, UpdateTruckRequest

router = APIRouter(prefix="/trucks", tags=["trucks"])


def _to_response(truck: Truck) -> TruckResponse:
    return TruckResponse(
        id=str(truck.id),
        plate_number=truck.plate_number,
        max_weight=truck.capacity.max_weight,
        max_volume=truck.capacity.max_volume,
        status=truck.status.value,
        deleted_at=truck.deleted_at.isoformat() if truck.deleted_at else None,
    )


@router.get("", response_model=PaginatedTruckResponse)
def list_trucks(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, description="Tìm theo biển số. Nhiều từ khóa cách nhau bằng dấu phẩy"),
    statuses: list[int] | None = Query(None, description="Lọc theo status: ?statuses=0&statuses=1&statuses=2"),
    include_deleted: bool = Query(False),
    truck_repo: TruckRepository = Depends(get_truck_repo),
    _: None = Depends(require_admin),
) -> PaginatedTruckResponse:
    query = TruckQuery(
        page=page,
        page_size=size,
        search=search,
        statuses=[TruckStatus(s) for s in statuses] if statuses else None,
        include_deleted=include_deleted,
    )
    result = truck_use_cases.list_trucks(query, truck_repo)
    return PaginatedTruckResponse(
        items=[_to_response(t) for t in result.items],
        total=result.total,
        page=result.page,
        size=result.size,
        pages=result.pages,
    )


@router.get("/{truck_id}", response_model=TruckResponse)
def get_truck(
    truck_id: str,
    truck_repo: TruckRepository = Depends(get_truck_repo),
    _: None = Depends(require_admin),
) -> TruckResponse:
    try:
        truck = truck_use_cases.get_truck(UUID(truck_id), truck_repo)
    except TruckNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    return _to_response(truck)


@router.post("", response_model=TruckResponse, status_code=201)
def create_truck(
    body: CreateTruckRequest,
    truck_repo: TruckRepository = Depends(get_truck_repo),
    _: None = Depends(require_admin),
) -> TruckResponse:
    truck = Truck(
        id=UUID(body.id),
        plate_number=body.plate_number,
        capacity=Capacity(max_weight=body.max_weight, max_volume=body.max_volume),
        status=TruckStatus.AVAILABLE,
    )
    try:
        created = truck_use_cases.create_truck(truck, truck_repo)
    except ValidationFailed as e:
        raise HTTPException(status_code=422, detail=str(e))
    return _to_response(created)


@router.put("/{truck_id}", response_model=TruckResponse)
def update_truck(
    truck_id: str,
    body: UpdateTruckRequest,
    truck_repo: TruckRepository = Depends(get_truck_repo),
    _: None = Depends(require_admin),
) -> TruckResponse:
    uid = UUID(truck_id)
    updated = Truck(
        id=uid,
        plate_number=body.plate_number,
        capacity=Capacity(max_weight=body.max_weight, max_volume=body.max_volume),
        status=TruckStatus(body.status),
    )
    try:
        result = truck_use_cases.update_truck(uid, updated, truck_repo)
    except ValidationFailed as e:
        raise HTTPException(status_code=422, detail=str(e))
    except TruckNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    return _to_response(result)


@router.delete("/{truck_id}", status_code=204)
def delete_truck(
    truck_id: str,
    truck_repo: TruckRepository = Depends(get_truck_repo),
    _: None = Depends(require_admin),
) -> None:
    try:
        truck_use_cases.delete_truck(UUID(truck_id), truck_repo)
    except TruckNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))