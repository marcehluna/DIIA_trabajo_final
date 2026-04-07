"""Cliente de chat vía API HTTP compatible con el SDK `openai` (Ollama, vLLM, cloud, etc.)."""

from __future__ import annotations

from regatas_assistant.config import Settings
from regatas_assistant.llm.base import LLMClient


class OpenAIChatClient(LLMClient):
    def __init__(self, settings: Settings):
        from openai import OpenAI

        if not settings.llm_api_key:
            raise ValueError(
                "REGATAS_LLM_API_KEY es obligatorio para REGATAS_LLM_BACKEND=openai "
                "(también acepta OPENAI_API_KEY por compatibilidad; en Ollama local podés usar `ollama`)."
            )
        self._client = OpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url or None,
        )
        self._model = settings.llm_model

    def complete(self, system_prompt: str, user_content: str) -> str:
        r = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            temperature=0.2,
        )
        choice = r.choices[0].message.content
        return (choice or "").strip()
