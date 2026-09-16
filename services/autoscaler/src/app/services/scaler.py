import logging
from datetime import datetime, timedelta
from typing import Optional

from kubernetes import client, config

from app.core.config import settings
from app.services.metrics import MetricsService

logger = logging.getLogger(__name__)


class ScalerService:
    def __init__(self):
        try:
            config.load_incluster_config()
        except config.ConfigException:
            config.load_kube_config()

        self.apps_v1 = client.AppsV1Api()
        self.metrics = MetricsService()
        self.last_scale_up: Optional[datetime] = None
        self.last_scale_down: Optional[datetime] = None

    def get_current_replicas(self) -> int:
        """Get current replica count."""
        try:
            deployment = self.apps_v1.read_namespaced_deployment(
                name=settings.TARGET_DEPLOYMENT, namespace=settings.TARGET_NAMESPACE
            )
            return deployment.spec.replicas or 1
        except Exception as e:
            logger.error(f"Error getting replicas: {e}")
            return 1

    def scale(self, replicas: int) -> bool:
        """Scale the deployment to the specified replica count."""
        try:
            replicas = max(settings.MIN_REPLICAS, min(settings.MAX_REPLICAS, replicas))

            self.apps_v1.patch_namespaced_deployment_scale(
                name=settings.TARGET_DEPLOYMENT,
                namespace=settings.TARGET_NAMESPACE,
                body={"spec": {"replicas": replicas}},
            )

            logger.info(f"Scaled {settings.TARGET_DEPLOYMENT} to {replicas} replicas")
            return True
        except Exception as e:
            logger.error(f"Error scaling deployment: {e}")
            return False

    def calculate_target_replicas(self) -> tuple[int, str]:
        """Calculate target replicas based on metrics."""
        current = self.get_current_replicas()

        queue_depth = self.metrics.get_queue_depth()
        kv_cache = self.metrics.get_kv_cache_utilization()
        p95_latency = self.metrics.get_p95_latency()
        tokens_per_sec = self.metrics.get_tokens_per_second()
        active_requests = self.metrics.get_active_requests()

        logger.info(
            f"Metrics: queue_depth={queue_depth}, kv_cache={kv_cache}%, "
            f"p95_latency={p95_latency}s, tokens/s={tokens_per_sec}, "
            f"active_requests={active_requests}"
        )

        # Scale up conditions
        scale_up_reasons = []

        if queue_depth > settings.QUEUE_DEPTH_THRESHOLD:
            scale_up_reasons.append(f"queue_depth={queue_depth}")

        if kv_cache > settings.KV_CACHE_THRESHOLD:
            scale_up_reasons.append(f"kv_cache={kv_cache}%")

        if p95_latency > settings.P95_LATENCY_THRESHOLD:
            scale_up_reasons.append(f"p95_latency={p95_latency}s")

        if scale_up_reasons:
            # Check cooldown
            if self.last_scale_up:
                elapsed = (datetime.now() - self.last_scale_up).total_seconds()
                if elapsed < settings.SCALE_UP_COOLDOWN:
                    logger.info(
                        f"Scale up cooldown active ({elapsed}s < {settings.SCALE_UP_COOLDOWN}s)"
                    )
                    return current, "cooldown"

            target = min(current + 1, settings.MAX_REPLICAS)
            if target > current:
                self.last_scale_up = datetime.now()
                return target, f"scale_up: {', '.join(scale_up_reasons)}"

        # Scale down conditions
        scale_down_conditions = [
            queue_depth <= settings.QUEUE_DEPTH_LOW,
            kv_cache < settings.KV_CACHE_LOW,
            p95_latency < settings.P95_LATENCY_LOW,
        ]

        if all(scale_down_conditions) and current > settings.MIN_REPLICAS:
            if self.last_scale_down:
                elapsed = (datetime.now() - self.last_scale_down).total_seconds()
                if elapsed < settings.SCALE_DOWN_COOLDOWN:
                    logger.info(
                        f"Scale down cooldown active ({elapsed}s < {settings.SCALE_DOWN_COOLDOWN}s)"
                    )
                    return current, "cooldown"

            target = max(current - 1, settings.MIN_REPLICAS)
            if target < current:
                self.last_scale_down = datetime.now()
                return target, "scale_down: all metrics low"

        return current, "no_change"

    def reconcile(self) -> dict:
        """Main reconciliation loop."""
        current = self.get_current_replicas()
        target, reason = self.calculate_target_replicas()

        if target != current:
            success = self.scale(target)
            return {
                "current": current,
                "target": target,
                "reason": reason,
                "success": success,
            }

        return {
            "current": current,
            "target": current,
            "reason": reason,
            "success": True,
        }
