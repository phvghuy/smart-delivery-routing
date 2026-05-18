from fastapi import APIRouter, Depends
from pydantic import BaseModel

from smart_delivery_routing.domain.repositories import DriverRepository
from ..dependencies import get_current_driver_id, get_driver_repo, require_driver

router = APIRouter(prefix="/drivers", tags=["drivers"])


class UpdateFCMTokenRequest(BaseModel):
    fcm_token: str


@router.post("/fcm-token", status_code=204)
def update_fcm_token(
    body: UpdateFCMTokenRequest,
    driver_id: str = Depends(get_current_driver_id),
    driver_repo: DriverRepository = Depends(get_driver_repo),
    _: None = Depends(require_driver),
) -> None:
    driver_repo.update_fcm_token(driver_id, body.fcm_token)
