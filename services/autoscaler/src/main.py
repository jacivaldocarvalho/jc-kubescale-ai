from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
import logging
import time
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.routes import router
from app.services.metrics import MetricsService
from app.services.scaler import ScalerService

logger = setup_logging()

SCALE_EVENTS = Counter(
    "autoscaler_scale_events_total", "Scale events", ["direction", "reason"]
)
CURRENT_REPLICAS = Gauge("autoscaler_current_replicas", "Current replicas")
TARGET_REPLICAS = Gauge("autoscaler_target_replicas", "Target replicas")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("JC-KubeScale Autoscaler starting")
    logger.info(f"Settings: {settings.model_dump()}")
    yield
    logger.info("JC-KubeScale Autoscaler shutting down")


app = FastAPI(
    title="JC-KubeScale Autoscaler",
    description="LLM-aware autoscaling for JC-KubeScale AI",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(router)


@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": time.time()}


@app.get("/ready")
async def ready():
    return {"status": "ready"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
