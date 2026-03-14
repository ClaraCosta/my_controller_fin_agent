import httpx

from backend.app.core.config import settings


class OllamaService:
    def generate(self, prompt: str) -> str:
        payload = {"model": settings.ollama_model, "prompt": prompt, "stream": False}
        try:
            response = httpx.post(f"{settings.ollama_base_url}/api/generate", json=payload, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()
        except Exception:
            return ""

