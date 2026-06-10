from celery import Celery

from smart_delivery_routing.config import REDIS_URL

celery_app = Celery(
    "smart_delivery_routing",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["smart_delivery_routing.infrastructure.celery.tasks"],
)

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
