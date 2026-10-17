from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ModelVersion(BaseModel):
    name: str = Field(..., description="Nome do modelo")
    version: str = Field(..., description="Versao do modelo")
    status: str = Field("loading", description="Status: ready, loading, error, deprecated")
    path: Optional[str] = Field(None, description="Caminho do modelo")
    size: Optional[str] = Field(None, description="Tamanho do modelo")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ModelRegistryResponse(BaseModel):
    models: List[ModelVersion]


class ModelVersionResponse(BaseModel):
    model: ModelVersion


class ModelStatusUpdate(BaseModel):
    status: str = Field(..., description="Novo status do modelo")
