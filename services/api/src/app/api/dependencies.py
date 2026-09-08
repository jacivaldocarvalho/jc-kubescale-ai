from functools import lru_cache
from app.services.inference import InferenceService


@lru_cache()
def get_inference_service():
    return InferenceService()
