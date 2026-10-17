from fastapi import APIRouter, HTTPException, BackgroundTasks
import logging

from app.services.rollout import RolloutService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1")


@router.get("/canary")
def get_canary():
    """Get current canary percentage"""
    rollout = RolloutService()
    return {"canary": rollout.get_current_canary()}


@router.post("/canary/{percentage}")
def set_canary(percentage: int):
    """Set canary percentage"""
    if percentage < 0 or percentage > 100:
        raise HTTPException(
            status_code=400, detail="Percentage must be between 0 and 100"
        )

    rollout = RolloutService()
    success = rollout.set_canary(percentage)
    return {"success": success, "canary": percentage}


@router.post("/rollout")
def start_rollout(background_tasks: BackgroundTasks):
    """Start a progressive rollout in background"""
    rollout = RolloutService()
    background_tasks.add_task(rollout.start_rollout)
    return {
        "status": "started",
        "message": "Rollout started in background",
        "stages": rollout.stages,
    }


@router.post("/rollback")
def rollback():
    """Rollback to stable version"""
    rollout = RolloutService()
    success = rollout.rollback()
    return {"success": success, "canary": 0}
