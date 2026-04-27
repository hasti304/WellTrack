"""
OpenAI-compatible chat completions for multiple providers (same HTTP shape as OpenAI /v1/chat/completions).

Uses the legacy ``openai`` 0.28 client: set ``api_key`` + ``api_base`` then ``ChatCompletion.create``.
"""
from typing import List, Optional, Tuple

import openai
from django.conf import settings


_PROVIDER_PRESETS = {
    "openai": ("https://api.openai.com/v1", "gpt-3.5-turbo"),
    "openrouter": ("https://openrouter.ai/api/v1", "openai/gpt-3.5-turbo"),
    "sambanova": ("https://api.sambanova.ai/v1", ""),
    "cerebras": ("https://api.cerebras.ai/v1", ""),
}


def resolve_llm() -> Tuple[str, str, str]:
    """
    Returns (api_key, api_base, model).
    """
    provider = (getattr(settings, "LLM_PROVIDER", "openai") or "openai").lower().strip()
    presets = _PROVIDER_PRESETS
    if provider not in presets:
        provider = "openai"

    default_base, default_model = presets[provider]
    base = (getattr(settings, "LLM_API_BASE", "") or "").strip().rstrip("/")
    if not base:
        base = default_base

    model = (getattr(settings, "LLM_MODEL", "") or "").strip()
    if not model:
        model = default_model

    key = (getattr(settings, "LLM_API_KEY", "") or "").strip()
    if not key:
        return "", base, model

    if provider in ("sambanova", "cerebras") and not (getattr(settings, "LLM_MODEL", "") or "").strip():
        return key, base, ""

    return key, base, model


def chat_completion(messages: List[dict]) -> Tuple[Optional[str], Optional[str]]:
    """
    Run a chat completion. ``messages`` is OpenAI-style role/content list.

    Returns (assistant_text, error_message).
    """
    api_key, api_base, model = resolve_llm()
    if not api_key:
        return None, "No LLM API key configured. Set LLM_API_KEY or OPENAI_API_KEY in .env."

    provider = (getattr(settings, "LLM_PROVIDER", "openai") or "openai").lower().strip()
    if provider in ("sambanova", "cerebras") and not model:
        return (
            None,
            f"Set LLM_MODEL in .env for provider '{provider}' (copy the exact model id from "
            f"{ 'https://cloud.sambanova.ai/apis' if provider == 'sambanova' else 'https://www.cerebras.ai/' } / your dashboard).",
        )

    openai.api_key = api_key
    openai.api_base = api_base

    try:
        resp = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=0.7,
        )
        text = resp.choices[0].message["content"]
        return (text.strip() if text else ""), None
    except Exception as exc:  # noqa: BLE001
        return None, str(exc)
