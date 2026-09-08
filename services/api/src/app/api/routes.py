from fastapi import APIRouter, HTTPException, Depends
import logging

from app.api.models import (
    ChatRequest,
    ChatResponse,
    CompletionRequest,
    CompletionResponse,
)
from app.api.dependencies import get_inference_service
from app.services.inference import InferenceService
from app.models.schemas import ModelInfo, ModelsResponse, Usage

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1")


@router.get("/models", response_model=ModelsResponse)
async def list_models():
    inference = InferenceService()
    models = await inference.list_models()
    return ModelsResponse(models=models)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, inference: InferenceService = Depends(get_inference_service)):
    try:
        response = await inference.chat(
            message=request.message,
            model=request.model,
            temperature=request.temperature or 0.7,
            max_tokens=request.max_tokens or 512,
        )
        return response
    except Exception as e:
        logger.error(f"Chat error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/completions", response_model=CompletionResponse)
async def completions(
    request: CompletionRequest,
    inference: InferenceService = Depends(get_inference_service),
):
    try:
        response = await inference.completions(
            prompt=request.prompt,
            model=request.model,
            max_tokens=request.max_tokens or 100,
            temperature=request.temperature or 0.7,
        )
        return response
    except Exception as e:
        logger.error(f"Completion error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
