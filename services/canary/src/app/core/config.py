from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    API_TITLE: str = "JC-KubeScale Canary Controller"
    API_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Target
    TARGET_NAMESPACE: str = "jc-kubescale"
    TARGET_DEPLOYMENT: str = "jc-kubescale-api"

    # Canary stages
    CANARY_STAGES: str = "10,50,100"
    CANARY_INTERVAL: int = 60
    CANARY_ERROR_THRESHOLD: float = 0.05
    CANARY_LATENCY_THRESHOLD: float = 2.0

    # Prometheus
    PROMETHEUS_URL: str = "http://prometheus-server.observability.svc.cluster.local:80"

    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
