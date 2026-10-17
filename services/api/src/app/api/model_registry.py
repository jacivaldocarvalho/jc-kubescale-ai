from fastapi import APIRouter, HTTPException
import logging

from app.models.registry import (
    ModelVersion,
    ModelRegistryResponse,
    ModelVersionResponse,
    ModelStatusUpdate,
)
from app.services.model_registry import ModelRegistryService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/models", tags=["models"])


@router.get("", response_model=ModelRegistryResponse)
def list_models():
    """Lista todos os modelos registrados"""
    registry = ModelRegistryService()
    return registry.list_models()


@router.get("/{name}", response_model=ModelRegistryResponse)
def get_model_versions(name: str):
    """Lista todas as versoes de um modelo"""
    registry = ModelRegistryService()
    versions = registry.get_versions(name)
    if not versions:
        raise HTTPException(status_code=404, detail=f"Model {name} not found")
    return ModelRegistryResponse(models=versions)


@router.get("/{name}/versions/{version}", response_model=ModelVersionResponse)
def get_model(name: str, version: str):
    """Retorna um modelo especifico"""
    registry = ModelRegistryService()
    model = registry.get_model(name, version)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model {name}:{version} not found")
    return ModelVersionResponse(model=model)


@router.post("", response_model=ModelVersionResponse)
def register_model(model: ModelVersion):
    """Registra um novo modelo"""
    registry = ModelRegistryService()
    registered = registry.register_model(model)
    return ModelVersionResponse(model=registered)


@router.patch("/{name}/versions/{version}/status", response_model=ModelVersionResponse)
def update_status(name: str, version: str, update: ModelStatusUpdate):
    """Atualiza o status de um modelo"""
    registry = ModelRegistryService()
    model = registry.update_status(name, version, update.status)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model {name}:{version} not found")
    return ModelVersionResponse(model=model)


@router.delete("/{name}/versions/{version}")
def delete_model(name: str, version: str):
    """Remove um modelo"""
    registry = ModelRegistryService()
    success = registry.delete_model(name, version)
    if not success:
        raise HTTPException(status_code=404, detail=f"Model {name}:{version} not found")
    return {"status": "deleted", "model": name, "version": version}
