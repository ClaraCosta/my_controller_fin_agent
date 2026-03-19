import base64
import mimetypes
from pathlib import Path

import httpx

from backend.app.core.config import settings


class OllamaService:
    def generate(self, prompt: str) -> str:
        with httpx.Client(timeout=30.0) as client:
            model_name = self._resolve_model_name(client)
            for endpoint, payload_builder, parser in (
                ("/api/generate", self._build_generate_payload, self._parse_generate_response),
                ("/api/chat", self._build_chat_payload, self._parse_chat_response),
                ("/v1/chat/completions", self._build_openai_chat_payload, self._parse_openai_chat_response),
            ):
                try:
                    response = client.post(
                        f"{settings.ollama_base_url}{endpoint}",
                        json=payload_builder(prompt, model_name),
                        headers=self._build_headers(endpoint),
                    )
                    response.raise_for_status()
                    content = parser(response.json())
                    if content:
                        return content
                except Exception:
                    continue
        return ""

    def extract_text_from_image(self, image_path: str) -> str:
        input_path = Path(image_path)
        if not input_path.exists() or not input_path.is_file():
            return ""

        mime_type = mimetypes.guess_type(str(input_path))[0] or "image/png"
        if not mime_type.startswith("image/"):
            return ""

        image_b64 = base64.b64encode(input_path.read_bytes()).decode("utf-8")
        prompt = (
            "Extraia o texto legível desta imagem de documento brasileiro. "
            "Retorne somente a transcrição limpa do texto, preservando números, valores, CNPJ, CPF, datas, "
            "campos manuscritos e nomes do estabelecimento. Não explique nada, não resuma, não invente, "
            "não corrija além do que for claramente visível."
        )

        with httpx.Client(timeout=60.0) as client:
            model_name = self._resolve_model_name(client, preferred_model=settings.ollama_vision_model)
            for endpoint, payload_builder, parser in (
                ("/api/chat", self._build_multimodal_chat_payload, self._parse_chat_response),
                ("/v1/chat/completions", self._build_openai_multimodal_payload, self._parse_openai_chat_response),
            ):
                try:
                    response = client.post(
                        f"{settings.ollama_base_url}{endpoint}",
                        json=payload_builder(prompt, model_name, image_b64, mime_type),
                        headers=self._build_headers(endpoint),
                    )
                    response.raise_for_status()
                    content = parser(response.json())
                    if content:
                        return content
                except Exception:
                    continue
        return ""

    @staticmethod
    def _build_generate_payload(prompt: str, model_name: str) -> dict:
        return {"model": model_name, "prompt": prompt, "stream": False}

    @staticmethod
    def _build_chat_payload(prompt: str, model_name: str) -> dict:
        return {
            "model": model_name,
            "stream": False,
            "messages": [{"role": "user", "content": prompt}],
        }

    @staticmethod
    def _build_openai_chat_payload(prompt: str, model_name: str) -> dict:
        return {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        }

    @staticmethod
    def _build_multimodal_chat_payload(prompt: str, model_name: str, image_b64: str, mime_type: str) -> dict:
        return {
            "model": model_name,
            "stream": False,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                    "images": [image_b64],
                }
            ],
        }

    @staticmethod
    def _build_openai_multimodal_payload(prompt: str, model_name: str, image_b64: str, mime_type: str) -> dict:
        return {
            "model": model_name,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{image_b64}"}},
                    ],
                }
            ],
            "stream": False,
        }

    def _resolve_model_name(self, client: httpx.Client, preferred_model: str | None = None) -> str:
        available_models = self._list_available_models(client)
        if preferred_model and preferred_model in available_models:
            return preferred_model
        if not available_models:
            return preferred_model or settings.ollama_model
        if settings.ollama_model in available_models:
            return settings.ollama_model
        return available_models[0]

    def _list_available_models(self, client: httpx.Client) -> list[str]:
        for endpoint, parser in (
            ("/api/tags", self._parse_api_tags_models),
            ("/v1/models", self._parse_openai_models),
        ):
            try:
                response = client.get(
                    f"{settings.ollama_base_url}{endpoint}",
                    headers=self._build_headers(endpoint),
                )
                response.raise_for_status()
                models = parser(response.json())
                if models:
                    return models
            except Exception:
                continue
        return []

    @staticmethod
    def _build_headers(endpoint: str) -> dict:
        if endpoint.startswith("/v1/"):
            return {"Authorization": "Bearer ollama"}
        return {}

    @staticmethod
    def _parse_generate_response(data: dict) -> str:
        return data.get("response", "").strip()

    @staticmethod
    def _parse_chat_response(data: dict) -> str:
        message = data.get("message") or {}
        return (message.get("content") or "").strip()

    @staticmethod
    def _parse_openai_chat_response(data: dict) -> str:
        choices = data.get("choices") or []
        if not choices:
            return ""
        message = choices[0].get("message") or {}
        return (message.get("content") or "").strip()

    @staticmethod
    def _parse_api_tags_models(data: dict) -> list[str]:
        return [item.get("model") for item in data.get("models", []) if item.get("model")]

    @staticmethod
    def _parse_openai_models(data: dict) -> list[str]:
        return [item.get("id") for item in data.get("data", []) if item.get("id")]
