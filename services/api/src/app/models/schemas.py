from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class Usage(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0


class ChatResponse(BaseModel):
    model: str
    response: str
    usage: Usage
    metadata: Optional[Dict[str, Any]] = None


class CompletionResponse(BaseModel):
    model: str
    text: str
    usage: Usage


class ModelInfo(BaseModel):
    name: str
    version: str
    status: str
    metadata: Optional[Dict[str, Any]] = None


class ModelsResponse(BaseModel):
    models: List[ModelInfo]
