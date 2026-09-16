import httpx
import logging
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class MetricsService:
    def __init__(self):
        self.prometheus_url = settings.PROMETHEUS_URL
        self.client = httpx.Client(timeout=10.0)

    def query(self, query: str) -> Optional[float]:
        """Query Prometheus and return a single value."""
        try:
            response = self.client.get(
                f"{self.prometheus_url}/api/v1/query", params={"query": query}
            )
            response.raise_for_status()
            data = response.json()

            if data["status"] != "success":
                return None

            results = data["data"]["result"]
            if not results:
                return None

            return float(results[0]["value"][1])
        except Exception as e:
            logger.error(f"Error querying Prometheus: {e}")
            return None

    def get_queue_depth(self) -> float:
        """Get current queue depth."""
        return self.query("sum(queue_depth)") or 0.0

    def get_kv_cache_utilization(self) -> float:
        """Get KV cache utilization percentage."""
        return self.query("avg(kv_cache_utilization)") or 0.0

    def get_p95_latency(self) -> float:
        """Get P95 latency in seconds."""
        return (
            self.query(
                "histogram_quantile(0.95, rate(http_request_latency_seconds_bucket[5m]))"
            )
            or 0.0
        )

    def get_tokens_per_second(self) -> float:
        """Get tokens per second."""
        return self.query("rate(tokens_output_total[1m])") or 0.0

    def get_active_requests(self) -> float:
        """Get active requests."""
        return self.query("http_active_requests") or 0.0
