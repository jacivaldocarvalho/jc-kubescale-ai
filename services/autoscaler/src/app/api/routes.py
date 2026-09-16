from fastapi import APIRouter, HTTPException
import logging

from app.services.scaler import ScalerService
from app.services.metrics import MetricsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1")


@router.get("/metrics")
async def get_metrics():
    """Get current metrics."""
    metrics = MetricsService()
    return {
        "queue_depth": metrics.get_queue_depth(),
        "kv_cache_utilization": metrics.get_kv_cache_utilization(),
        "p95_latency": metrics.get_p95_latency(),
        "tokens_per_second": metrics.get_tokens_per_second(),
        "active_requests": metrics.get_active_requests(),
    }


@router.get("/replicas")
async def get_replicas():
    """Get current replica count."""
    scaler = ScalerService()
    return {"replicas": scaler.get_current_replicas()}


@router.post("/reconcile")
async def reconcile():
    """Trigger reconciliation loop."""
    try:
        scaler = ScalerService()
        return scaler.reconcile()
    except Exception as e:
        logger.error(f"Reconcile error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scale")
async def scale(replicas: int):
    """Manually scale to specified replicas."""
    try:
        scaler = ScalerService()
        success = scaler.scale(replicas)
        return {"success": success, "replicas": replicas}
    except Exception as e:
        logger.error(f"Scale error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
