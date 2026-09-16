from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # API
    API_TITLE: str = "JC-KubeScale Autoscaler"
    API_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Target
    TARGET_NAMESPACE: str = "jc-kubescale"
    TARGET_DEPLOYMENT: str = "jc-kubescale-api"
    MIN_REPLICAS: int = 1
    MAX_REPLICAS: int = 10

    # Scaling thresholds
    QUEUE_DEPTH_THRESHOLD: int = 5
    KV_CACHE_THRESHOLD: float = 80.0
    P95_LATENCY_THRESHOLD: float = 2.0
    TOKENS_PER_SECOND_THRESHOLD: float = 100.0

    # Scale down thresholds
    QUEUE_DEPTH_LOW: int = 1
    KV_CACHE_LOW: float = 30.0
    P95_LATENCY_LOW: float = 0.5

    # Cooldown
    SCALE_UP_COOLDOWN: int = 60
    SCALE_DOWN_COOLDOWN: int = 300

    # Prometheus
    PROMETHEUS_URL: str = "http://prometheus-server.observability.svc.cluster.local:80"

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
