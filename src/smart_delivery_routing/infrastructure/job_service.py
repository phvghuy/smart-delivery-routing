from uuid import UUID

from celery import Task
from celery.result import AsyncResult

from smart_delivery_routing.application.services import JobNotFound, JobService, JobStatus
from smart_delivery_routing.infrastructure.celery import celery_app
from smart_delivery_routing.infrastructure.celery.tasks import handle_shipping_request
from smart_delivery_routing.infrastructure.redis_client import job_exists


class CeleryRedisJobService(JobService):
    def submit(self, token: str) -> str:
        raise NotImplementedError

    def get_status(self, job_id: str) -> JobStatus:
        if not job_exists(job_id):
            raise JobNotFound(job_id)

        result = AsyncResult(job_id, app=celery_app)

        if result.state == "PENDING":
            if result.date_done is None:
                return JobStatus(job_id=job_id, status="pending")
            return JobStatus(job_id=job_id, status="expired")

        if result.state == "FAILURE":
            return JobStatus(job_id=job_id, status="failure", error=str(result.info))

        return JobStatus(job_id=job_id, status="success", result=result.result)

    def enqueue_process_shipping_request(self, request_id: UUID) -> None:
        task: Task = handle_shipping_request  # type: ignore[assignment]
        task.delay(str(request_id))
