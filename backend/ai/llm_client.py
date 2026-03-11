"""Ollama LLM client for free local inference."""
import httpx
import json
import asyncio
from typing import AsyncGenerator, Optional
from backend.config import get_settings

settings = get_settings()


class OllamaClient:
    """Client for interacting with Ollama local LLM."""
    
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
        self.client = httpx.AsyncClient(timeout=120.0)
    
    async def generate(self, prompt: str, system_prompt: str = "", temperature: float = 0.3) -> str:
        """Generate a completion from the LLM."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": 2048,
            }
        }
        try:
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json=payload,
            )
            response.raise_for_status()
            return response.json().get("response", "")
        except httpx.ConnectError:
            return "⚠️ Ollama is not running. Please start Ollama with `ollama serve` and pull a model with `ollama pull mistral`."
        except Exception as e:
            return f"⚠️ LLM Error: {str(e)}"
    
    async def generate_stream(self, prompt: str, system_prompt: str = "", temperature: float = 0.3) -> AsyncGenerator[str, None]:
        """Stream a completion from the LLM."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": 2048,
            }
        }
        try:
            async with self.client.stream(
                "POST",
                f"{self.base_url}/api/generate",
                json=payload,
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        data = json.loads(line)
                        if "response" in data:
                            yield data["response"]
                        if data.get("done", False):
                            break
        except httpx.ConnectError:
            yield "⚠️ Ollama is not running. Please start Ollama."
    
    async def chat(self, messages: list[dict], temperature: float = 0.3) -> str:
        """Chat completion with message history."""
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": 2048,
            }
        }
        try:
            response = await self.client.post(
                f"{self.base_url}/api/chat",
                json=payload,
            )
            response.raise_for_status()
            return response.json().get("message", {}).get("content", "")
        except httpx.ConnectError:
            return "⚠️ Ollama is not running."
        except Exception as e:
            return f"⚠️ LLM Error: {str(e)}"
    
    async def list_models(self) -> list[str]:
        """List available Ollama models."""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            models = response.json().get("models", [])
            return [m["name"] for m in models]
        except Exception:
            return []
    
    async def is_available(self) -> bool:
        """Check if Ollama is running."""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except Exception:
            return False


# Singleton
llm_client = OllamaClient()
