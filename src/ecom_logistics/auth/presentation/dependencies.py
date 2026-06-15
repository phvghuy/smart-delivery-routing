from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

from ecom_logistics.auth.application.services import AuthService
from ecom_logistics.app.dependencies import get_auth_service

_security = HTTPBearer()


def require_admin(
    token=Depends(_security),
    auth: AuthService = Depends(get_auth_service),
) -> None:
    if auth.get_user_role(token.credentials) != "admin":
        raise HTTPException(status_code=403, detail="Admin required.")


def require_driver(
    token=Depends(_security),
    auth: AuthService = Depends(get_auth_service),
) -> None:
    if auth.get_user_role(token.credentials) not in ("admin", "driver"):
        raise HTTPException(status_code=403, detail="Authentication required.")


def get_current_driver_id(
    token=Depends(_security),
    auth: AuthService = Depends(get_auth_service),
) -> str:
    return auth.get_user_id(token.credentials)
