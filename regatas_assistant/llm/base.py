"""Contrato del modelo de lenguaje."""

from __future__ import annotations

from abc import ABC, abstractmethod


class LLMClient(ABC):
    @abstractmethod
    def complete(self, system_prompt: str, user_content: str) -> str:
        """Devuelve texto del asistente (markdown)."""
        ...
