"""Cliente de chat HTTP (p. ej. `.../v1/chat/completions` en Ollama, vLLM u otros hosts compatibles)."""

from __future__ import annotations

from regatas_assistant.config import Settings
from regatas_assistant.llm.base import LLMClient
from regatas_assistant.ollama_models import list_installed_ollama_models, resolve_model_name


class HTTPChatClient(LLMClient):
    def __init__(self, settings: Settings):
        from openai import OpenAI

        if not settings.llm_api_key:
            raise ValueError(
                "REGATAS_LLM_API_KEY es obligatorio para REGATAS_LLM_BACKEND=http "
                "(en Ollama local podés usar `ollama`)."
            )
        self._client = OpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url or None,
            timeout=settings.llm_timeout_seconds,
        )
        self._base_url = settings.llm_base_url
        self._model = settings.llm_model

    def complete(
        self,
        system_prompt: str,
        user_content: str,
        *,
        model: str | None = None,
    ) -> str:
        use_model = (model or "").strip() or self._model
        if (model or "").strip():
            # Respetar el modelo elegido en la UI (dropdown Ollama).
            use_model = (model or "").strip()
        else:
            installed = list_installed_ollama_models(self._base_url)
            if installed:
                use_model = resolve_model_name(installed, use_model)
        r = self._client.chat.completions.create(
            model=use_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            temperature=0.2,
        )
        choice = r.choices[0].message.content
        return (choice or "").strip()
