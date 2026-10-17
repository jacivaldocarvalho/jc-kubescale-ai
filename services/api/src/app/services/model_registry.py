import logging
import json
from typing import Optional, List, Dict
from datetime import datetime
from threading import Lock, RLock
from kubernetes import client, config

from app.core.config import settings
from app.models.registry import ModelVersion, ModelRegistryResponse

logger = logging.getLogger(__name__)


class RegistryStorageError(RuntimeError):
    """Falha de persistencia com diagnostico seguro para o cliente."""

    def __init__(self, code: str, detail: str, status_code: int = 503):
        super().__init__(detail)
        self.code = code
        self.detail = detail
        self.status_code = status_code


def storage_error(exc: Exception) -> RegistryStorageError:
    status = getattr(exc, "status", None)
    if isinstance(exc, config.ConfigException):
        return RegistryStorageError(
            "kubernetes_configuration",
            "Registry indisponivel: configure as credenciais in-cluster ou um kubeconfig valido.",
        )
    if status in (401, 403):
        return RegistryStorageError(
            "kubernetes_access_denied",
            "Registry sem acesso ao Kubernetes. Verifique ServiceAccount, Role e RoleBinding no namespace configurado.",
        )
    if status == 404:
        return RegistryStorageError(
            "kubernetes_resource_missing",
            "Recurso Kubernetes ausente. Verifique o namespace configurado para o Registry.",
        )
    if status == 409:
        return RegistryStorageError(
            "registry_conflict",
            "O registro foi alterado durante a gravacao. Consulte novamente e repita a operacao.",
            status_code=409,
        )
    if isinstance(exc, (ValueError, TypeError, KeyError)):
        return RegistryStorageError(
            "registry_invalid_data",
            "O ConfigMap do Registry contem dados invalidos. Verifique models.json.",
        )
    return RegistryStorageError(
        "kubernetes_unavailable",
        "Registry indisponivel: nao foi possivel concluir o acesso ao Kubernetes.",
    )


class ModelRegistryService:
    _instance = None
    _instance_lock = Lock()
    _models: Dict[str, Dict[str, ModelVersion]] = {}
    _config_map_name = "model-registry"
    _config_map_namespace = "jc-kubescale"

    def __new__(cls):
        with cls._instance_lock:
            if cls._instance is None:
                instance = super().__new__(cls)
                instance._initialize()
                cls._instance = instance
        return cls._instance

    def _initialize(self):
        """Inicializa o cliente Kubernetes e carrega o registro persistido."""
        self._config_map_name = settings.MODEL_REGISTRY_CONFIGMAP
        self._config_map_namespace = settings.MODEL_REGISTRY_NAMESPACE
        self._mutation_lock = RLock()
        self._request_timeout = (3, 10)
        try:
            try:
                config.load_incluster_config()
            except config.ConfigException:
                config.load_kube_config()

            self.core_v1 = client.CoreV1Api()
            self._models = {}
            if not self._load_from_configmap():
                self._initialize_default_models()
        except RegistryStorageError:
            raise
        except Exception as exc:
            error = storage_error(exc)
            logger.error(
                "Registry initialization failed: code=%s namespace=%s configmap=%s kubernetes_status=%s",
                error.code,
                self._config_map_namespace,
                self._config_map_name,
                getattr(exc, "status", None),
                exc_info=True,
            )
            raise error from exc

    def _load_from_configmap(self) -> bool:
        """Carrega o registro, preservando inclusive um registro vazio."""
        try:
            cm = self.core_v1.read_namespaced_config_map(
                name=self._config_map_name,
                namespace=self._config_map_namespace,
                _request_timeout=self._request_timeout,
            )
        except client.exceptions.ApiException as exc:
            if exc.status == 404:
                logger.info("ConfigMap not found, starting with defaults")
                return False
            logger.exception("Error loading ConfigMap")
            raise

        if not cm.data or "models.json" not in cm.data:
            return False

        models_data = json.loads(cm.data["models.json"])
        if not isinstance(models_data, list):
            raise ValueError("models.json must contain a list")
        for model_data in models_data:
            model = ModelVersion(**model_data)
            self._models.setdefault(model.name, {})[model.version] = model
        logger.info("Loaded %s models from ConfigMap", len(models_data))
        return True

    def _save_to_configmap(self, models=None):
        """Salva o registro usando a versao atual do recurso Kubernetes."""
        try:
            models_data = [
                model.model_dump(mode="json")
                for versions in (self._models if models is None else models).values()
                for model in versions.values()
            ]
            cm = client.V1ConfigMap(
                metadata=client.V1ObjectMeta(
                    name=self._config_map_name,
                    namespace=self._config_map_namespace,
                ),
                data={"models.json": json.dumps(models_data)},
            )
            try:
                existing = self.core_v1.read_namespaced_config_map(
                    name=self._config_map_name,
                    namespace=self._config_map_namespace,
                    _request_timeout=self._request_timeout,
                )
            except client.exceptions.ApiException as exc:
                if exc.status != 404:
                    raise
                self.core_v1.create_namespaced_config_map(
                    namespace=self._config_map_namespace,
                    body=cm,
                    _request_timeout=self._request_timeout,
                )
            else:
                existing.data = dict(existing.data or {})
                existing.data["models.json"] = cm.data["models.json"]
                self.core_v1.replace_namespaced_config_map(
                    name=self._config_map_name,
                    namespace=self._config_map_namespace,
                    body=existing,
                    _request_timeout=self._request_timeout,
                )
            logger.info("Models saved to ConfigMap")
        except Exception as exc:
            error = storage_error(exc)
            logger.error(
                "Registry save failed: code=%s namespace=%s configmap=%s kubernetes_status=%s",
                error.code,
                self._config_map_namespace,
                self._config_map_name,
                getattr(exc, "status", None),
                exc_info=True,
            )
            raise error from exc

    def _initialize_default_models(self):
        """Inicializa modelos padrao quando nao ha registro persistido."""
        if self._models:
            return
        default_models = [
            ModelVersion(
                name="qwen",
                version="1",
                status="ready",
                path="/models/qwen-v1",
                size="7B",
                metadata={"description": "Qwen 7B - Versao base"},
            ),
            ModelVersion(
                name="qwen",
                version="2",
                status="ready",
                path="/models/qwen-v2",
                size="7B",
                metadata={"description": "Qwen 7B - Versao melhorada"},
            ),
            ModelVersion(
                name="qwen-small",
                version="1",
                status="ready",
                path="/models/qwen-small",
                size="1.8B",
                metadata={"description": "Qwen 1.8B - Versao leve"},
            ),
            ModelVersion(
                name="qwen-large",
                version="1",
                status="ready",
                path="/models/qwen-large",
                size="14B",
                metadata={"description": "Qwen 14B - Versao grande"},
            ),
        ]

        for model in default_models:
            if model.name not in self._models:
                self._models[model.name] = {}
            self._models[model.name][model.version] = model

        logger.info(f"Model registry initialized with {len(default_models)} models")
        self._save_to_configmap()

    def list_models(self) -> ModelRegistryResponse:
        """Lista todos os modelos e versoes"""
        models = []
        for name, versions in self._models.items():
            for version, model in versions.items():
                models.append(model)
        return ModelRegistryResponse(models=models)

    def get_model(self, name: str, version: str) -> Optional[ModelVersion]:
        """Retorna um modelo especifico"""
        versions = self._models.get(name, {})
        return versions.get(version)

    def get_versions(self, name: str) -> List[ModelVersion]:
        """Lista todas as versoes de um modelo"""
        versions = self._models.get(name, {})
        return list(versions.values())

    def register_model(self, model: ModelVersion) -> ModelVersion:
        """Registra um novo modelo"""
        with self._mutation_lock:
            registered = model.model_copy(deep=True)
            registered.updated_at = datetime.now()
            models = {name: dict(versions) for name, versions in self._models.items()}
            models.setdefault(registered.name, {})[registered.version] = registered
            self._save_to_configmap(models)
            self._models = models
            logger.info(f"Registered model: {registered.name}:{registered.version}")
            return registered

    def update_status(self, name: str, version: str, status: str) -> Optional[ModelVersion]:
        """Atualiza o status de um modelo"""
        with self._mutation_lock:
            model = self.get_model(name, version)
            if model is None:
                return None
            updated = model.model_copy(deep=True)
            updated.status = status
            updated.updated_at = datetime.now()
            models = {key: dict(versions) for key, versions in self._models.items()}
            models[name][version] = updated
            self._save_to_configmap(models)
            self._models = models
            logger.info(f"Updated status: {name}:{version} -> {status}")
            return updated

    def delete_model(self, name: str, version: str) -> bool:
        """Remove um modelo"""
        with self._mutation_lock:
            if self.get_model(name, version) is None:
                return False
            models = {key: dict(versions) for key, versions in self._models.items()}
            del models[name][version]
            if not models[name]:
                del models[name]
            self._save_to_configmap(models)
            self._models = models
            logger.info(f"Deleted model: {name}:{version}")
            return True
