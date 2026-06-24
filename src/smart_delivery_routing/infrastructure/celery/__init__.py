from celery import Celery
from celery.signals import worker_process_init

from smart_delivery_routing.config import REDIS_URL

celery_app = Celery(
    "smart_delivery_routing",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["smart_delivery_routing.infrastructure.celery.tasks"],
)


@worker_process_init.connect
def init_worker_telemetry(**kwargs) -> None:
    # Khởi tạo OTel trong mỗi worker process — signal này chạy sau khi worker fork
    from smart_delivery_routing.infrastructure.telemetry import setup_worker_telemetry
    setup_worker_telemetry()

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    result_expires=86400,
    beat_schedule={
        "create-delivery-routes": {
            "task": "create_delivery_routes",
            "schedule": 1800.0,  # 30 phút
        },
    },
    timezone="Asia/Ho_Chi_Minh",
)
