import httpx
from app.providers.interfaces import ReasoningProvider, VisionLanguageProvider
from app.core.config import settings

class OllamaReasoningProvider(ReasoningProvider):
    def generate(self, prompt: str) -> str:
        client = httpx.Client(timeout=settings.OLLAMA_TIMEOUT)
        response = client.post(
            f"{settings.OLLAMA_BASE_URL}/api/generate",
            json={
                "model": settings.OLLAMA_REASONING_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.0}
            }
        )
        response.raise_for_status()
        return response.json().get("response", "")

class OllamaVisionProvider(VisionLanguageProvider):
    def analyze(self, image_data: bytes, prompt: str) -> str:
        import base64
        b64_image = base64.b64encode(image_data).decode('utf-8')
        
        client = httpx.Client(timeout=settings.OLLAMA_TIMEOUT)
        response = client.post(
            f"{settings.OLLAMA_BASE_URL}/api/generate",
            json={
                "model": settings.OLLAMA_VISION_MODEL,
                "prompt": prompt,
                "images": [b64_image],
                "stream": False,
                "options": {"temperature": 0.0}
            }
        )
        response.raise_for_status()
        return response.json().get("response", "")
