from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import os


@dataclass
class Settings:
    """Runtime configuration loaded from environment variables.

    Env vars (with defaults):
    - WATCHTOWER_LLM_PROVIDER: str = "openai"
    - WATCHTOWER_LLM_MODEL: str = "gpt-4o-mini"
    - OPENAI_API_KEY: str = ""
    - OPENAI_BASE_URL: Optional[str] = None
    - WATCHTOWER_TEMPERATURE: float = 0.1
    - WATCHTOWER_MAX_OUTPUT_TOKENS: int = 800
    """

    provider: str = "openai"
    model: str = "gpt-4o-mini"
    api_key: str = ""
    base_url: Optional[str] = None
    temperature: float = 0.1
    max_output_tokens: int = 800

    @staticmethod
    def from_env() -> "Settings":
        s = Settings()
        s.provider = os.getenv("WATCHTOWER_LLM_PROVIDER", s.provider)
        s.model = os.getenv("WATCHTOWER_LLM_MODEL", s.model)
        s.api_key = os.getenv("OPENAI_API_KEY", "")
        s.base_url = os.getenv("OPENAI_BASE_URL") or None
        try:
            s.temperature = float(os.getenv("WATCHTOWER_TEMPERATURE", s.temperature))
        except Exception:
            pass
        try:
            s.max_output_tokens = int(
                os.getenv("WATCHTOWER_MAX_OUTPUT_TOKENS", s.max_output_tokens)
            )
        except Exception:
            pass
        return s


def print_settings(settings: Settings) -> None:
    base_url = settings.base_url or "https://api.openai.com/v1"
    print(f"Provider: {settings.provider}")
    print(f"Model: {settings.model}")
    print(f"Base URL: {base_url}")
    print(f"Temperature: {settings.temperature}")
    print(f"Max output tokens: {settings.max_output_tokens}")
