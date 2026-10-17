import logging
import time
from typing import Optional, List
from datetime import datetime

from kubernetes import client, config

from app.core.config import settings
from app.services.metrics import MetricsService

logger = logging.getLogger(__name__)


class RolloutService:
    def __init__(self):
        try:
            config.load_incluster_config()
        except config.ConfigException:
            config.load_kube_config()

        self.apps_v1 = client.AppsV1Api()
        self.metrics = MetricsService()
        self.stages = [int(s) for s in settings.CANARY_STAGES.split(",")]

    def get_current_canary(self) -> int:
        """Get current canary percentage from deployment annotation"""
        try:
            deployment = self.apps_v1.read_namespaced_deployment(
                name=settings.TARGET_DEPLOYMENT, namespace=settings.TARGET_NAMESPACE
            )
            annotations = deployment.metadata.annotations or {}
            return int(annotations.get("jc-kubescale/canary", "0"))
        except Exception as e:
            logger.error(f"Error getting canary: {e}")
            return 0

    def set_canary(self, percentage: int) -> bool:
        """Set canary percentage in deployment annotation"""
        try:
            self.apps_v1.patch_namespaced_deployment(
                name=settings.TARGET_DEPLOYMENT,
                namespace=settings.TARGET_NAMESPACE,
                body={
                    "metadata": {
                        "annotations": {"jc-kubescale/canary": str(percentage)}
                    }
                },
            )
            logger.info(f"Canary set to {percentage}%")
            return True
        except Exception as e:
            logger.error(f"Error setting canary: {e}")
            return False

    def check_health(self) -> bool:
        """Check if current canary is healthy"""
        error_rate = self.metrics.get_error_rate()
        p95_latency = self.metrics.get_p95_latency()

        logger.info(f"Health check: error_rate={error_rate}, p95_latency={p95_latency}")

        if error_rate > settings.CANARY_ERROR_THRESHOLD:
            logger.warning(f"Error rate too high: {error_rate}")
            return False

        if p95_latency > settings.CANARY_LATENCY_THRESHOLD:
            logger.warning(f"Latency too high: {p95_latency}")
            return False

        return True

    def rollback(self) -> bool:
        """Rollback to stable version"""
        logger.warning("Rolling back canary to 0%")
        return self.set_canary(0)

    def start_rollout(self) -> dict:
        """Start a progressive rollout"""
        logger.info("Starting canary rollout")

        results = []
        for stage in self.stages:
            logger.info(f"Deploying canary at {stage}%")

            if not self.set_canary(stage):
                return {
                    "status": "failed",
                    "stage": stage,
                    "reason": "set_canary failed",
                }

            # Wait for the interval
            time.sleep(settings.CANARY_INTERVAL)

            # Check health
            if not self.check_health():
                logger.error(f"Health check failed at {stage}%")
                self.rollback()
                return {
                    "status": "rolled_back",
                    "stage": stage,
                    "reason": "health check failed",
                }

            results.append({"stage": stage, "status": "healthy"})

        logger.info("Rollout completed successfully")
        return {"status": "completed", "stages": results}
