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

    def get_error_rate(self) -> float:
        return (
            self.query(
                "sum(rate(http_requests_total{status=~'5..'}[5m])) / sum(rate(http_requests_total[5m]))"
            )
            or 0.0
        )

    def get_p95_latency(self) -> float:
        return (
            self.query(
                "max(histogram_quantile(0.95, sum(rate(http_request_latency_seconds_bucket[5m])) by (le)))"
            )
            or 0.0
        )
