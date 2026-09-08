from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ChatRequest(BaseModel):
    message: str = Field(..., description="Mensagem para o modelo")
    model: Optional[str] = Field("qwen", description="Nome do modelo")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(512, ge=1, le=4096)
    stream: Optional[bool] = Field(False, description="Streaming response")


class Usage(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0


class ChatResponse(BaseModel):
    model: str
    response: str
    usage: Usage
    metadata: Optional[Dict[str, Any]] = None


class CompletionRequest(BaseModel):
    prompt: str = Field(..., description="Prompt para completar")
    model: Optional[str] = Field("qwen", description="Nome do modelo")
    max_tokens: Optional[int] = Field(100, ge=1, le=2048)
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0)


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
