from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import time
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

# OpenTelemetry imports
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.routes import router
from app.services.inference import InferenceService

# Setup logging
logger = setup_logging()

# Setup OpenTelemetry
if settings.OTLP_ENDPOINT:
    resource = Resource(attributes={SERVICE_NAME: "jc-kubescale-api"})
    provider = TracerProvider(resource=resource)
    processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=settings.OTLP_ENDPOINT, insecure=True))
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)

# ============================================
# Prometheus metrics
# ============================================
REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram(
    "http_request_latency_seconds", "HTTP request latency", ["method", "endpoint"]
)
ACTIVE_REQUESTS = Gauge("http_active_requests", "Active HTTP requests")
TOKENS_INPUT = Counter("tokens_input_total", "Total input tokens")
TOKENS_OUTPUT = Counter("tokens_output_total", "Total output tokens")
MODEL_LOAD_TIME = Histogram("model_load_time_seconds", "Model load time")

# ============================================
# Métricas específicas de LLM (para o KEDA)
# ============================================
QUEUE_DEPTH = Gauge("queue_depth", "Current queue depth")
KV_CACHE_UTILIZATION = Gauge("kv_cache_utilization", "KV cache utilization percentage")
TOKENS_PER_SECOND = Gauge("tokens_per_second", "Tokens per second")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("JC-KubeScale AI API starting")
    logger.info(f"Settings: {settings.model_dump()}")

    # Inicializar métricas de LLM
    QUEUE_DEPTH.set(0)
    KV_CACHE_UTILIZATION.set(0)
    TOKENS_PER_SECOND.set(0)

    yield
    logger.info("JC-KubeScale AI API shutting down")


app = FastAPI(
    title="JC-KubeScale AI API",
    description="Kubernetes-native AI Inference & Autoscaling Platform",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instrumentation with OpenTelemetry
if settings.OTLP_ENDPOINT:
    FastAPIInstrumentor.instrument_app(app)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    ACTIVE_REQUESTS.inc()

    # Simular queue depth durante a requisição
    current_queue = QUEUE_DEPTH._value.get()
    QUEUE_DEPTH.set(current_queue + 1)

    try:
        response = await call_next(request)
        latency = time.time() - start_time

        REQUEST_COUNT.labels(
            method=request.method, endpoint=request.url.path, status=response.status_code
        ).inc()

        REQUEST_LATENCY.labels(method=request.method, endpoint=request.url.path).observe(latency)

        # Simular KV cache e tokens após a requisição
        # KV cache aumenta 5% a cada requisição (até 95%)
        current_kv = KV_CACHE_UTILIZATION._value.get()
        KV_CACHE_UTILIZATION.set(min(95.0, current_kv + 5.0))

        # Tokens por segundo baseado na latência
        TOKENS_PER_SECOND.set(100.0 / max(latency, 0.001))

        return response
    finally:
        ACTIVE_REQUESTS.dec()
        # Decrementar queue depth após processar
        new_queue = max(0, QUEUE_DEPTH._value.get() - 1)
        QUEUE_DEPTH.set(new_queue)


app.include_router(router)


@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": time.time()}


@app.get("/ready")
async def ready():
    inference = InferenceService()
    ready_status = await inference.is_ready()
    return {"status": "ready" if ready_status else "not_ready", "inference": ready_status}


if __name__ == "__main__":

    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
