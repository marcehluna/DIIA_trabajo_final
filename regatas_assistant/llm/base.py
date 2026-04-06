"""Contrato del modelo de lenguaje."""

from __future__ import annotations

from abc import ABC, abstractmethod


class LLMClient(ABC):
    @abstractmethod
    def complete(
        self,
        system_prompt: str,
        user_content: str,
        *,
        model: str | None = None,
    ) -> str:
        """Devuelve texto del asistente (markdown). `model` solo aplica a backends que lo soporten."""
        ...
