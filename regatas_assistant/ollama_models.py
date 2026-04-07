"""Lista modelos instalados en Ollama vía API nativa `/api/tags`."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from urllib.parse import urlparse


def ollama_tags_url(openai_compat_base_url: str | None) -> str | None:
    """Pasa de la base tipo OpenAI (`.../v1`) al endpoint `.../api/tags` de Ollama."""
    if not openai_compat_base_url:
        return None
    u = openai_compat_base_url.strip().rstrip("/")
    if u.endswith("/v1"):
        root = u[:-3].rstrip("/")
        return f"{root}/api/tags"
    parsed = urlparse(u)
    if parsed.scheme and parsed.netloc:
        if parsed.port == 11434 or parsed.netloc.endswith(":11434"):
            return f"{parsed.scheme}://{parsed.netloc}/api/tags"
    return None


def list_installed_ollama_models(
    openai_compat_base_url: str | None,
    *,
    timeout: float = 5.0,
) -> list[str]:
    """Nombres de modelos locales reportados por Ollama (p. ej. `llama3:latest`)."""
    tags_url = ollama_tags_url(openai_compat_base_url)
    if not tags_url:
        return []
    try:
        req = urllib.request.Request(tags_url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.load(resp)
    except (
        urllib.error.URLError,
        urllib.error.HTTPError,
        TimeoutError,
        json.JSONDecodeError,
        OSError,
    ):
        return []
    models = payload.get("models") if isinstance(payload, dict) else None
    if not isinstance(models, list):
        return []
    names: list[str] = []
    for m in models:
        if isinstance(m, dict):
            n = m.get("name")
            if isinstance(n, str) and n.strip():
                names.append(n.strip())
    return sorted(set(names))


def default_choice(installed: list[str], env_model: str) -> str:
    if env_model in installed:
        return env_model
    if installed:
        return installed[0]
    return env_model
