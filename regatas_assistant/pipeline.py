"""Orquestación: corpus → recuperación → prompt → LLM."""

from __future__ import annotations

from regatas_assistant.config import Settings
from regatas_assistant.ingestion import format_chunks_for_prompt, load_corpus_chunks
from regatas_assistant.llm.base import LLMClient
from regatas_assistant.llm.openai_compat import OpenAIChatClient
from regatas_assistant.llm.stub import StubLLMClient
from regatas_assistant.prompts import SYSTEM_PROMPT, USER_TEMPLATE
from regatas_assistant.rag.retriever import CorpusRetriever, build_retriever


def _build_llm(settings: Settings) -> LLMClient:
    backend = settings.llm_backend
    if backend == "stub":
        return StubLLMClient()
    if backend == "openai":
        return OpenAIChatClient(settings)
    raise ValueError(
        f"REGATAS_LLM_BACKEND desconocido: {backend}. Use stub | openai."
    )


def _compose_query(relato_protesta: str, relato_protestado: str | None) -> str:
    parts = [relato_protesta.strip()]
    if relato_protestado and relato_protestado.strip():
        parts.append(relato_protestado.strip())
    return "\n\n".join(parts)


class ProtestPipeline:
    def __init__(
        self,
        settings: Settings,
        retriever: CorpusRetriever,
        llm: LLMClient,
    ):
        self.settings = settings
        self.retriever = retriever
        self.llm = llm

    @classmethod
    def from_settings(cls, settings: Settings) -> ProtestPipeline:
        chunks = load_corpus_chunks(settings)
        inner = build_retriever(settings, chunks)
        retriever = CorpusRetriever(inner, settings.retrieve_top_k)
        llm = _build_llm(settings)
        return cls(settings, retriever, llm)

    @classmethod
    def from_env(cls) -> ProtestPipeline:
        return cls.from_settings(Settings.from_env())

    def analyze(self, relato_protesta: str, relato_protestado: str | None) -> str:
        query = _compose_query(relato_protesta, relato_protestado)
        retrieved = self.retriever.retrieve(query)
        context = format_chunks_for_prompt(retrieved)
        protestado_block = (
            relato_protestado.strip()
            if relato_protestado and relato_protestado.strip()
            else "No se proporcionó relato del barco protestado."
        )
        user_content = USER_TEMPLATE.format(
            context=context,
            relato_protesta=relato_protesta.strip(),
            relato_protestado=protestado_block,
        )
        return self.llm.complete(SYSTEM_PROMPT, user_content)
