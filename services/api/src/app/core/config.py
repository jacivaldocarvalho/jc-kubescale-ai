from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # API
    API_TITLE: str = "JC-KubeScale AI API"
    API_VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    # Inference
    INFERENCE_ENDPOINT: str = "http://localhost:8080"
    INFERENCE_TIMEOUT: int = 60
    MODEL_NAME: str = "qwen"
    MODEL_VERSION: str = "1"
    
    # Observability
    OTLP_ENDPOINT: Optional[str] = "otel-collector.observability.svc.cluster.local:4317"
    LOG_LEVEL: str = "INFO"
    
    # Auth
    AUTH_ENABLED: bool = False
    JWT_SECRET: Optional[str] = None
    JWT_ALGORITHM: str = "HS256"
    
    # Rate limiting
    RATE_LIMIT_ENABLED: bool = False
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
