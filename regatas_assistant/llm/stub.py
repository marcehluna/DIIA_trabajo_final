"""LLM simulado para probar Gradio y el flujo sin API."""

from __future__ import annotations

from regatas_assistant.llm.base import LLMClient
from regatas_assistant.prompts import STUB_LLM_NOTICE


class StubLLMClient(LLMClient):
    def complete(self, system_prompt: str, user_content: str) -> str:
        preview = user_content.strip()
        if len(preview) > 1200:
            preview = preview[:1200] + "\n\n[… contenido truncado en vista previa del stub …]"
        return (
            "## 1. Síntesis fáctica (hechos encontrados)\n\n"
            "(Modo stub) Revisá los relatos ingresados y el contexto normativo recuperado "
            "en el mensaje del usuario. El motor RAG ya seleccionó fragmentos del Call Book "
            "y del Case Book; al activar un LLM real se generará aquí la reconstrucción objetiva "
            "del incidente y el último punto de certeza.\n\n"
            "## 2. Identificación normativa jerarquizada\n\n"
            "(Modo stub) Listado preliminar: pendiente de análisis con LLM. "
            "Usá las citas entre corchetes del contexto recuperado como ancla normativa.\n\n"
            "## 3. Rationale técnico (razonamiento lógico)\n\n"
            "(Modo stub) Sin modelo activo no se aplica cadena de razonamiento sobre reglas "
            "y Calls.\n\n"
            "## 4. Dictamen de resolución\n\n"
            "(Modo stub) Sin decisión sugerida. En local: Ollama + `REGATAS_LLM_BACKEND=http` "
            "(por defecto ya apunta a Llama 3 vía API compatible).\n\n"
            "### Vista previa del prompt de usuario (referencia)\n\n"
            f"```\n{preview}\n```"
            + STUB_LLM_NOTICE
        )
