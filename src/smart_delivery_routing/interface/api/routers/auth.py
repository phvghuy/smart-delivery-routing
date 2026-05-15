from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer

from smart_delivery_routing.application.services import AuthService
from ..dependencies import get_auth_service
from ..schemas import LoginRequest, LoginResponse

router = APIRouter(prefix="/auth", tags=["auth"])
_security = HTTPBearer()


@router.post("/login", response_model=LoginResponse)
def login(
    body: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> LoginResponse:
    try:
        token = auth_service.sign_in(body.email, body.password)
        return LoginResponse(access_token=token.access_token, role=token.role)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid credentials.")


@router.post("/logout", status_code=204)
def logout(
    token=Depends(_security),
    auth_service: AuthService = Depends(get_auth_service),
) -> None:
    auth_service.sign_out(token.credentials)
