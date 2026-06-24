import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def _init_provider() -> None:
    # Khởi tạo TracerProvider — dùng chung cho cả API và Celery worker
    resource = Resource.create({
        "service.name": os.getenv("OTEL_SERVICE_NAME", "smart-delivery-routing"),
    })
    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"),
        insecure=True,
    )
    # BatchSpanProcessor gom spans lại rồi gửi một lần, giảm overhead network
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)


def setup_telemetry(app) -> None:
    _init_provider()
    # Tự động tạo span cho mỗi HTTP request vào FastAPI và call ra ngoài qua httpx
    FastAPIInstrumentor.instrument_app(app)
    HTTPXClientInstrumentor().instrument()


def setup_worker_telemetry() -> None:
    # Gọi trong Celery worker — không cần FastAPI/httpx instrumentation
    _init_provider()