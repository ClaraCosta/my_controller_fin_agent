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

    def _resolve_model_name(self, client: httpx.Client) -> str:
        available_models = self._list_available_models(client)
        if not available_models:
            return settings.ollama_model
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
