from fastapi import APIRouter, Depends, HTTPException

from smart_delivery_routing.application.services import JobNotFound, JobService
from ..dependencies import get_job_service, require_admin
from ..schemas import JobStatusResponse

router = APIRouter(tags=["jobs"])


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
def get_job(
    job_id: str,
    _: None = Depends(require_admin),
    job_service: JobService = Depends(get_job_service),
) -> JobStatusResponse:
    try:
        status = job_service.get_status(job_id)
    except JobNotFound:
        raise HTTPException(status_code=404, detail="Job not found.")

    return JobStatusResponse(
        job_id=status.job_id,
        status=status.status,
        result=status.result,
        error=status.error,
    )
