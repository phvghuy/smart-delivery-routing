from fastapi import APIRouter, Depends

from smart_delivery_routing.application import vehicle_use_cases
from smart_delivery_routing.domain.models import Vehicle
from smart_delivery_routing.domain.repositories import VehicleRepository
from ..dependencies import get_vehicle_repo, require_admin, require_driver
from ..schemas import CreateVehicleRequest, UpdateVehicleRequest, VehicleResponse

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


def _to_response(vehicle: Vehicle) -> VehicleResponse:
    return VehicleResponse(
        vehicle_id=vehicle.vehicle_id,
        current_warehouse_id=vehicle.current_warehouse_id,
        max_weight=vehicle.max_weight,
        max_volume=vehicle.max_volume,
    )


@router.get("", response_model=list[VehicleResponse])
def list_vehicles(
    vehicle_repo: VehicleRepository = Depends(get_vehicle_repo),
    _: None = Depends(require_driver),
) -> list[VehicleResponse]:
    return [_to_response(v) for v in vehicle_use_cases.list_vehicles(vehicle_repo)]


@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(
    vehicle_id: str,
    vehicle_repo: VehicleRepository = Depends(get_vehicle_repo),
    _: None = Depends(require_driver),
) -> VehicleResponse:
    return _to_response(vehicle_use_cases.get_vehicle(vehicle_id, vehicle_repo))


@router.post("", response_model=VehicleResponse, status_code=201)
def create_vehicle(
    body: CreateVehicleRequest,
    vehicle_repo: VehicleRepository = Depends(get_vehicle_repo),
    _: None = Depends(require_admin),
) -> VehicleResponse:
    vehicle = Vehicle(
        vehicle_id=body.vehicle_id,
        current_warehouse_id=body.current_warehouse_id,
        max_weight=body.max_weight,
        max_volume=body.max_volume,
    )
    return _to_response(vehicle_use_cases.create_vehicle(vehicle, vehicle_repo))


@router.put("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(
    vehicle_id: str,
    body: UpdateVehicleRequest,
    vehicle_repo: VehicleRepository = Depends(get_vehicle_repo),
    _: None = Depends(require_admin),
) -> VehicleResponse:
    vehicle = Vehicle(
        vehicle_id=vehicle_id,
        current_warehouse_id=body.current_warehouse_id,
        max_weight=body.max_weight,
        max_volume=body.max_volume,
    )
    return _to_response(vehicle_use_cases.update_vehicle(vehicle_id, vehicle, vehicle_repo))


@router.delete("/{vehicle_id}", status_code=204)
def delete_vehicle(
    vehicle_id: str,
    vehicle_repo: VehicleRepository = Depends(get_vehicle_repo),
    _: None = Depends(require_admin),
) -> None:
    vehicle_use_cases.delete_vehicle(vehicle_id, vehicle_repo)
