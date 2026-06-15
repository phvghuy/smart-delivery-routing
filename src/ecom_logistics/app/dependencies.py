from functools import lru_cache

from fastapi import Depends
from fastapi.security import HTTPBearer
from supabase import Client, create_client

from ecom_logistics.auth.application.services import AuthService
from ecom_logistics.auth.infrastructure.repositories import SupabaseAuthService
from ecom_logistics.config import SUPABASE_KEY, SUPABASE_SERVICE_KEY, SUPABASE_URL
from ecom_logistics.linehaul.hub.domain import HubRepository
from ecom_logistics.linehaul.hub.infrastructure import SupabaseHubRepository, SupabaseHubQueryRepository

_security = HTTPBearer()


@lru_cache
def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)


@lru_cache
def get_supabase_service_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def get_auth_service() -> AuthService:
    return SupabaseAuthService(get_supabase_service_client())


def _authed_client(token: str) -> Client:
    client = get_supabase_client()
    client.postgrest.auth(token)
    return client


def get_hub_repo(token=Depends(_security)) -> HubRepository:
    return SupabaseHubRepository(_authed_client(token.credentials))


def get_hub_query_repo(token=Depends(_security)) -> SupabaseHubQueryRepository:
    return SupabaseHubQueryRepository(_authed_client(token.credentials))
