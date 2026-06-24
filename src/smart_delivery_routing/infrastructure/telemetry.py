import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def setup_telemetry(app) -> None:
    # Khai báo tên service hiện thị trong Jaeger UI
    resource = Resource.create({
        "service.name": os.getenv("OTEL_SERVICE_NAME", "smart-delivery-routing"),
    })

    # Khởi tạo provider và cấu hình xuất traces sang Jaeger qua gRPC
    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"),
        insecure=True,  # không dùng TLS trong môi trường local
    )
    # BatchSpanProcessor gom nhiều spans lại rồi gửi một lần, giảm overhead
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    # Tự động tạo span cho mỗi HTTP request vào FastAPI và call ra ngoài qua httpx
    FastAPIInstrumentor.instrument_app(app)
    HTTPXClientInstrumentor().instrument()