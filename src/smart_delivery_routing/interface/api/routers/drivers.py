from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from smart_delivery_routing.application import driver_use_cases
from smart_delivery_routing.application.driver_use_cases import DriverNotDeletable, DriverNotFound, ValidationFailed
from smart_delivery_routing.domain.delivery import Driver, DriverProfile, DriverQuery, DriverRepository, DriverStatus
from smart_delivery_routing.domain.shared import Capacity
from ..dependencies import get_driver_repo, get_current_driver_id, require_admin, require_driver
from ..schemas import CreateDriverRequest, DriverResponse, PaginatedDriverResponse, UpdateDriverRequest, UpdateFCMTokenRequest

router = APIRouter(prefix="/drivers", tags=["drivers"])


def _to_response(driver: Driver) -> DriverResponse:
    return DriverResponse(
        id=str(driver.id),
        name=driver.profile.name,
        phone=driver.profile.phone,
        plate_number=driver.profile.plate_number,
        current_hub_id=str(driver.current_hub_id),
        hub_name=driver.hub_name,
        max_weight=driver.capacity.max_weight,
        max_volume=driver.capacity.max_volume,
        status=driver.status.value,
        fcm_token=driver.fcm_token,
        deleted_at=driver.deleted_at.isoformat() if driver.deleted_at else None,
    )


@router.get("", response_model=PaginatedDriverResponse)
def list_drivers(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, description="Tìm theo tên, SĐT, biển số. Nhiều từ khóa cách nhau bằng dấu phẩy"),
    statuses: list[int] | None = Query(None, description="Lọc theo status (có thể chọn nhiều): ?statuses=1&statuses=2"),
    include_deleted: bool = Query(False),
    driver_repo: DriverRepository = Depends(get_driver_repo),
    _: None = Depends(require_admin),
) -> PaginatedDriverResponse:
    query = DriverQuery(
        page=page,
        page_size=size,
        search=search,
        statuses=[DriverStatus(s) for s in statuses] if statuses else None,
        include_deleted=include_deleted,
    )
    result = driver_use_cases.list_drivers(query, driver_repo)
    return PaginatedDriverResponse(
        items=[_to_response(d) for d in result.items],
        total=result.total,
        page=result.page,
        size=result.size,
        pages=result.pages,
    )


@router.get("/{driver_id}", response_model=DriverResponse)
def get_driver(
    driver_id: str,
    driver_repo: DriverRepository = Depends(get_driver_repo),
    _: None = Depends(require_admin),
) -> DriverResponse:
    try:
        driver = driver_use_cases.get_driver(UUID(driver_id), driver_repo)
    except DriverNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    return _to_response(driver)


@router.post("", response_model=DriverResponse, status_code=201)
def create_driver(
    body: CreateDriverRequest,
    driver_repo: DriverRepository = Depends(get_driver_repo),
    _: None = Depends(require_admin),
) -> DriverResponse:
    driver = Driver(
        id=UUID(body.id),
        profile=DriverProfile(name=body.name, phone=body.phone, plate_number=body.plate_number),
        current_hub_id=UUID(body.current_hub_id),
        capacity=Capacity(max_weight=body.max_weight, max_volume=body.max_volume),
        status=DriverStatus.AVAILABLE,
        fcm_token=body.fcm_token,
    )
    try:
        created = driver_use_cases.create_driver(driver, driver_repo)
    except ValidationFailed as e:
        raise HTTPException(status_code=422, detail=str(e))
    return _to_response(created)


@router.put("/{driver_id}", response_model=DriverResponse)
def update_driver(
    driver_id: str,
    body: UpdateDriverRequest,
    driver_repo: DriverRepository = Depends(get_driver_repo),
    _: None = Depends(require_admin),
) -> DriverResponse:
    uid = UUID(driver_id)
    updated = Driver(
        id=uid,
        profile=DriverProfile(name=body.name, phone=body.phone, plate_number=body.plate_number),
        current_hub_id=UUID(body.current_hub_id),
        capacity=Capacity(max_weight=body.max_weight, max_volume=body.max_volume),
        status=DriverStatus(body.status),
        fcm_token=body.fcm_token,
    )
    try:
        result = driver_use_cases.update_driver(uid, updated, driver_repo)
    except ValidationFailed as e:
        raise HTTPException(status_code=422, detail=str(e))
    except DriverNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    return _to_response(result)


@router.delete("/{driver_id}", status_code=204)
def delete_driver(
    driver_id: str,
    driver_repo: DriverRepository = Depends(get_driver_repo),
    _: None = Depends(require_admin),
) -> None:
    try:
        driver_use_cases.delete_driver(UUID(driver_id), driver_repo)
    except DriverNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DriverNotDeletable as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/fcm-token", status_code=204)
def update_fcm_token(
    body: UpdateFCMTokenRequest,
    driver_id: str = Depends(get_current_driver_id),
    driver_repo: DriverRepository = Depends(get_driver_repo),
    _: None = Depends(require_driver),
) -> None:
    driver_repo.update_fcm_token(driver_id, body.fcm_token)