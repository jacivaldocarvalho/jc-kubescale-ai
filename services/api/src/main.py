from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import time
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
)
from starlette.responses import Response

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.routes import router
from app.services.inference import InferenceService

# Setup logging
logger = setup_logging()

# Prometheus metrics
REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram(
    "http_request_latency_seconds", "HTTP request latency", ["method", "endpoint"]
)
ACTIVE_REQUESTS = Gauge("http_active_requests", "Active HTTP requests")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("JC-KubeScale AI API starting")
    logger.info(f"Settings: {settings.model_dump()}")
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


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    ACTIVE_REQUESTS.inc()

    try:
        response = await call_next(request)
        latency = time.time() - start_time

        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code,
        ).inc()

        REQUEST_LATENCY.labels(method=request.method, endpoint=request.url.path).observe(latency)

        return response
    finally:
        ACTIVE_REQUESTS.dec()


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
    return {
        "status": "ready" if ready_status else "not_ready",
        "inference": ready_status,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
