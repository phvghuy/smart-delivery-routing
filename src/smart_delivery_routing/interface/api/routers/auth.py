from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer

from smart_delivery_routing.infrastructure.supabase.repositories.auth import sign_in, sign_out
from ..schemas import LoginRequest, LoginResponse

router = APIRouter(prefix="/auth", tags=["auth"])
_security = HTTPBearer()


@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest) -> LoginResponse:
    try:
        result = sign_in(body.email, body.password)
        role = result.user.app_metadata.get("role", "")
        return LoginResponse(access_token=result.session.access_token, role=role)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid credentials.")


@router.post("/logout", status_code=204)
def logout(token=Depends(_security)) -> None:
    sign_out(token.credentials)
