from __future__ import annotations

import json
from typing import Any, Dict
import requests

from .config import Settings


class LLMClient:
    """Minimal, provider-pluggable LLM client.

    For now, implements OpenAI-compatible Chat Completions over HTTP.
    """

    def __init__(self, settings: Settings) -> None:
        if not settings.api_key:
            raise RuntimeError("OPENAI_API_KEY not set in environment.")
        self.settings = settings
        self.base_url = settings.base_url or "https://api.openai.com/v1"
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {settings.api_key}",
                "Content-Type": "application/json",
            }
        )

    def chat(self, system: str, user: str) -> str:
        """Return raw text from a chat completion."""
        payload: Dict[str, Any] = {
            "model": self.settings.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": self.settings.temperature,
            "max_tokens": self.settings.max_output_tokens,
            # Encourage JSON when relevant; ignored if free-form answer
            "response_format": {"type": "text"},
        }
        resp = self.session.post(
            f"{self.base_url}/chat/completions", json=payload, timeout=120
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()

    def chat_json(self, system: str, user: str) -> Dict[str, Any]:
        """Attempt to parse the model output as JSON; fall back to a 'raw' field."""
        # Nudge model to return JSON
        payload: Dict[str, Any] = {
            "model": self.settings.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": self.settings.temperature,
            "max_tokens": self.settings.max_output_tokens,
            "response_format": {"type": "json_object"},
        }
        resp = self.session.post(
            f"{self.base_url}/chat/completions", json=payload, timeout=180
        )
        resp.raise_for_status()
        data = resp.json()
        text = data["choices"][0]["message"]["content"].strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"raw": text}
