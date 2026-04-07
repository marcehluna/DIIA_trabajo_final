"""Recuperación de fragmentos: léxica (sin embeddings) o semántica (OpenAI / local)."""

from __future__ import annotations

import math
import re
from abc import ABC, abstractmethod
from typing import Sequence

import numpy as np

from regatas_assistant.config import Settings
from regatas_assistant.ingestion import TextChunk


def _tokenize(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-zA-ZáéíóúñÁÉÍÓÚÑ]{3,}", text.lower())}


class BaseRetriever(ABC):
    @abstractmethod
    def retrieve(self, query: str, top_k: int) -> list[TextChunk]:
        ...


class LexicalRetriever(BaseRetriever):
    def __init__(self, chunks: Sequence[TextChunk]):
        self._chunks = list(chunks)
        self._vocab = [_tokenize(c.text) for c in self._chunks]

    def retrieve(self, query: str, top_k: int) -> list[TextChunk]:
        q = _tokenize(query)
        if not q:
            return self._chunks[:top_k]
        scores: list[tuple[float, int]] = []
        for i, vocab in enumerate(self._vocab):
            inter = len(q & vocab)
            if inter == 0:
                continue
            # BM25-ish: crude idf using log(N/df)
            df = sum(1 for v in self._vocab if q & v)
            idf = math.log((len(self._chunks) + 1) / (df + 1)) + 1.0
            scores.append((inter * idf, i))
        scores.sort(key=lambda x: -x[0])
        picked = [self._chunks[i] for _, i in scores[:top_k]]
        if len(picked) < top_k:
            seen = {id(c) for c in picked}
            for c in self._chunks:
                if len(picked) >= top_k:
                    break
                if id(c) not in seen:
                    picked.append(c)
                    seen.add(id(c))
        return picked


def _cosine_top_k(
    query_vec: np.ndarray, matrix: np.ndarray, top_k: int
) -> list[int]:
    q = query_vec.astype(np.float64)
    nq = np.linalg.norm(q)
    if nq == 0:
        return list(range(min(top_k, matrix.shape[0])))
    q = q / nq
    sims = matrix @ q
    k = min(top_k, len(sims))
    idx = np.argpartition(-sims, k - 1)[:k]
    idx = idx[np.argsort(-sims[idx])]
    return idx.tolist()


class SemanticRetrieverWithEncoder(BaseRetriever):
    def __init__(
        self,
        chunks: Sequence[TextChunk],
        vectors: np.ndarray,
        encode_query,
    ):
        self._chunks = list(chunks)
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self._vectors = vectors / norms
        self._encode_query = encode_query

    def retrieve(self, query: str, top_k: int) -> list[TextChunk]:
        qv = np.array(self._encode_query(query), dtype=np.float64)
        idx = _cosine_top_k(qv, self._vectors, top_k)
        return [self._chunks[i] for i in idx]


def build_retriever(settings: Settings, chunks: list[TextChunk]) -> BaseRetriever:
    backend = settings.embedding_backend
    if backend == "lexical":
        return LexicalRetriever(chunks)

    if backend == "openai":
        from regatas_assistant.rag.embeddings_openai import (
            OpenAIEmbeddingEncoder,
            embed_corpus_openai,
        )

        if not settings.llm_api_key:
            raise ValueError(
                "REGATAS_EMBEDDING_BACKEND=openai requiere REGATAS_LLM_API_KEY en el entorno "
                "(o OPENAI_API_KEY por compatibilidad)."
            )
        enc = OpenAIEmbeddingEncoder(settings)
        matrix = embed_corpus_openai(enc, [c.text for c in chunks])
        return SemanticRetrieverWithEncoder(
            chunks, matrix, lambda q: enc.embed_one(q)
        )

    if backend == "local":
        from regatas_assistant.rag.embeddings_local import (
            LocalSentenceEncoder,
            embed_corpus_local,
        )

        enc = LocalSentenceEncoder(settings.local_embedding_model)
        matrix = embed_corpus_local(enc, [c.text for c in chunks])
        return SemanticRetrieverWithEncoder(
            chunks, matrix, lambda q: enc.encode_query(q)
        )

    raise ValueError(
        f"REGATAS_EMBEDDING_BACKEND desconocido: {backend}. "
        "Use lexical | openai | local."
    )


class CorpusRetriever:
    """Fachada estable para el pipeline."""

    def __init__(self, inner: BaseRetriever, default_top_k: int):
        self._inner = inner
        self._default_top_k = default_top_k

    def retrieve(self, query: str, top_k: int | None = None) -> list[TextChunk]:
        k = top_k if top_k is not None else self._default_top_k
        return self._inner.retrieve(query, k)
