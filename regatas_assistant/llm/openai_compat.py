"""Cliente de chat compatible con OpenAI (también Azure OpenAI vía OPENAI_BASE_URL)."""

from __future__ import annotations

from regatas_assistant.config import Settings
from regatas_assistant.llm.base import LLMClient


class OpenAIChatClient(LLMClient):
    def __init__(self, settings: Settings):
        from openai import OpenAI

        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY es obligatorio para REGATAS_LLM_BACKEND=openai")
        self._client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url or None,
        )
        self._model = settings.openai_llm_model

    def complete(
        self,
        system_prompt: str,
        user_content: str,
        *,
        model: str | None = None,
    ) -> str:
        use_model = model if model else self._model
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
