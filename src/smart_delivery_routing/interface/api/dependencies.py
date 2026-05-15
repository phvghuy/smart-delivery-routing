from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from supabase import Client

from smart_delivery_routing.application.services import AuthService, DistanceCalculator, JobService, RouteSolver
from smart_delivery_routing.application.solvers.nearest_neighbor import NearestNeighborSolver
from smart_delivery_routing.config import OSRM_URL
from smart_delivery_routing.domain.repositories import OrderRepository, VehicleRepository, WarehouseRepository
from smart_delivery_routing.infrastructure.job_service import CeleryRedisJobService
from smart_delivery_routing.infrastructure.osrm.distance import OSRMDistanceCalculator
from smart_delivery_routing.infrastructure.supabase.auth_service import SupabaseAuthService
from smart_delivery_routing.infrastructure.supabase.client import get_supabase_client
from smart_delivery_routing.infrastructure.supabase.repositories.auth import get_user_role
from smart_delivery_routing.infrastructure.supabase.repositories.orders import SupabaseOrderRepository
from smart_delivery_routing.infrastructure.supabase.repositories.vehicles import SupabaseVehicleRepository
from smart_delivery_routing.infrastructure.supabase.repositories.warehouses import SupabaseWarehouseRepository

_distance_calculator = OSRMDistanceCalculator(base_url=OSRM_URL)
_solvers: list[tuple[str, RouteSolver]] = [("nearest_neighbor", NearestNeighborSolver())]
_job_service = CeleryRedisJobService()
_auth_service = SupabaseAuthService()

_security = HTTPBearer()


def _authed_client(token: str) -> Client:
    client = get_supabase_client()
    client.postgrest.auth(token)
    return client


def get_order_repo(token=Depends(_security)) -> OrderRepository:
    return SupabaseOrderRepository(_authed_client(token.credentials))


def get_vehicle_repo(token=Depends(_security)) -> VehicleRepository:
    return SupabaseVehicleRepository(_authed_client(token.credentials))


def get_warehouse_repo(token=Depends(_security)) -> WarehouseRepository:
    return SupabaseWarehouseRepository(_authed_client(token.credentials))


def require_admin(token=Depends(_security)) -> None:
    if get_user_role(token.credentials) != "admin":
        raise HTTPException(status_code=403, detail="Admin required.")


def require_driver(token=Depends(_security)) -> None:
    if get_user_role(token.credentials) not in ("admin", "driver"):
        raise HTTPException(status_code=403, detail="Authentication required.")


def get_distance_calculator() -> DistanceCalculator:
    return _distance_calculator


def get_solvers() -> list[tuple[str, RouteSolver]]:
    return _solvers


def get_job_service() -> JobService:
    return _job_service


def get_auth_service() -> AuthService:
    return _auth_service
