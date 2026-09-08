import logging
from typing import Optional, List

from app.core.config import settings
from app.models.schemas import ChatResponse, CompletionResponse, ModelInfo, Usage

logger = logging.getLogger(__name__)


class InferenceService:
    _instance = None
    _ready = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.base_url = settings.INFERENCE_ENDPOINT
        self.model_name = settings.MODEL_NAME
        self.model_version = settings.MODEL_VERSION

    async def is_ready(self) -> bool:
        self._ready = True
        return True

    async def chat(
        self,
        message: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> ChatResponse:
        # Mock para desenvolvimento
        responses = {
            "kubernetes": "Kubernetes e uma plataforma open-source para orquestracao de containers. "
            "Ela automatiza o deploy, scaling e gerenciamento de aplicacoes containerizadas. "
            "Kubernetes agrupa containers em pods para facilitar o gerenciamento.",
            "ia": "Inteligencia Artificial e um campo da computacao que busca criar sistemas capazes de "
            "realizar tarefas que normalmente requerem inteligencia humana.",
            "default": f"Voce perguntou sobre: {message}. Como modelo Qwen, processei sua mensagem "
            f"e estou respondendo de forma simulada para demonstracao do sistema.",
        }

        message_lower = message.lower()
        response_text = responses["default"]
        for key, resp in responses.items():
            if key in message_lower:
                response_text = resp
                break

        input_tokens = len(message.split())
        output_tokens = len(response_text.split())

        return ChatResponse(
            model=model or self.model_name,
            response=response_text,
            usage=Usage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens,
            ),
        )

    async def completions(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 100,
        temperature: float = 0.7,
    ) -> CompletionResponse:
        text = f"Completando: {prompt}... Este e um mock para demonstracao."
        input_tokens = len(prompt.split())
        output_tokens = len(text.split())

        return CompletionResponse(
            model=model or self.model_name,
            text=text,
            usage=Usage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens,
            ),
        )

    async def list_models(self) -> List[ModelInfo]:
        return [
            ModelInfo(
                name=self.model_name,
                version=self.model_version,
                status="ready" if self._ready else "loading",
            )
        ]
