from celery.result import AsyncResult

from smart_delivery_routing.application.services import JobNotFound, JobService, JobStatus
from smart_delivery_routing.infrastructure.celery import celery_app
from smart_delivery_routing.infrastructure.celery.tasks import run_optimize
from smart_delivery_routing.infrastructure.redis_client import job_exists, register_job


class CeleryRedisJobService(JobService):
    def submit(self, token: str) -> str:
        task = run_optimize.delay(token)
        register_job(task.id)
        return task.id

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
