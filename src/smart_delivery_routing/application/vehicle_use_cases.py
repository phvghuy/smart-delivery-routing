from dataclasses import dataclass

from smart_delivery_routing.domain.models import Vehicle
from smart_delivery_routing.domain.repositories import VehicleRepository
from smart_delivery_routing.domain.validators import validate_vehicle_fields

from .routing_use_cases import ValidationFailed


# --- Domain exceptions ---

@dataclass(frozen=True)
class VehicleNotFound(Exception):
    vehicle_id: str

    def __str__(self) -> str:
        return f"Vehicle '{self.vehicle_id}' not found."


@dataclass(frozen=True)
class VehicleAlreadyExists(Exception):
    vehicle_id: str

    def __str__(self) -> str:
        return f"Vehicle '{self.vehicle_id}' already exists."


# --- Use cases ---

def list_vehicles(repo: VehicleRepository) -> list[Vehicle]:
    return repo.get_vehicles()


def get_vehicle(vehicle_id: str, repo: VehicleRepository) -> Vehicle:
    vehicle = repo.get_vehicle_by_id(vehicle_id)
    if vehicle is None:
        raise VehicleNotFound(vehicle_id=vehicle_id)
    return vehicle


def create_vehicle(vehicle: Vehicle, repo: VehicleRepository) -> Vehicle:
    errors = validate_vehicle_fields(vehicle)
    if errors:
        raise ValidationFailed(errors)

    if repo.get_vehicle_by_id(vehicle.vehicle_id) is not None:
        raise VehicleAlreadyExists(vehicle_id=vehicle.vehicle_id)

    return repo.create_vehicle(vehicle)


def update_vehicle(vehicle_id: str, updated: Vehicle, repo: VehicleRepository) -> Vehicle:
    errors = validate_vehicle_fields(updated)
    if errors:
        raise ValidationFailed(errors)

    if repo.get_vehicle_by_id(vehicle_id) is None:
        raise VehicleNotFound(vehicle_id=vehicle_id)

    return repo.update_vehicle(updated)


def delete_vehicle(vehicle_id: str, repo: VehicleRepository) -> None:
    if repo.get_vehicle_by_id(vehicle_id) is None:
        raise VehicleNotFound(vehicle_id=vehicle_id)

    repo.delete_vehicle(vehicle_id)
