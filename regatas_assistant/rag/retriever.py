"""Recuperación de fragmentos: léxica, semántica (HTTP / local) o híbrida (RRF)."""

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


def chunk_bucket(chunk: TextChunk) -> str:
    """processed = RRS/definiciones JSONL; pdf = fragmentos de PDF."""
    if chunk.doc_type in ("rrs", "definition", "call", "case"):
        return "processed"
    return "pdf"


def split_chunks_by_doctype(
    chunks: Sequence[TextChunk],
) -> dict[str, list[TextChunk]]:
    """Agrupa por doc_type; desconocidos → pdf."""
    pools: dict[str, list[TextChunk]] = {
        "rrs": [],
        "call": [],
        "case": [],
        "definition": [],
        "pdf": [],
    }
    for c in chunks:
        dt = (c.doc_type or "pdf").lower()
        if dt not in pools:
            pools["pdf"].append(c)
        else:
            pools[dt].append(c)
    return pools


def split_chunks_by_bucket(
    chunks: Sequence[TextChunk],
) -> tuple[list[TextChunk], list[TextChunk]]:
    processed: list[TextChunk] = []
    pdf: list[TextChunk] = []
    for c in chunks:
        if chunk_bucket(c) == "processed":
            processed.append(c)
        else:
            pdf.append(c)
    return processed, pdf


def _dedupe_chunks(chunks: Sequence[TextChunk]) -> list[TextChunk]:
    seen: set[int] = set()
    out: list[TextChunk] = []
    for c in chunks:
        key = id(c)
        if key in seen:
            continue
        seen.add(key)
        out.append(c)
    return out


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


class HybridRetriever(BaseRetriever):
    """Fusiona ranking léxico y semántico con RRF (compatible con cupos vía inner_builder)."""

    def __init__(
        self,
        chunks: Sequence[TextChunk],
        lexical: LexicalRetriever,
        semantic: BaseRetriever,
        *,
        rrf_k: int = 60,
        candidate_multiplier: int = 2,
    ):
        self._chunks = list(chunks)
        self._lexical = lexical
        self._semantic = semantic
        self._rrf_k = max(1, rrf_k)
        self._mult = max(1, candidate_multiplier)

    def retrieve(self, query: str, top_k: int) -> list[TextChunk]:
        if not self._chunks:
            return []
        k = max(1, top_k)
        n_cand = min(len(self._chunks), k * self._mult)
        lex_hits = self._lexical.retrieve(query, n_cand)
        sem_hits = self._semantic.retrieve(query, n_cand)
        scores: dict[int, float] = {}
        chunk_by_id: dict[int, TextChunk] = {}

        def _add_ranked(hits: list[TextChunk]) -> None:
            for rank, chunk in enumerate(hits):
                cid = id(chunk)
                chunk_by_id[cid] = chunk
                scores[cid] = scores.get(cid, 0.0) + 1.0 / (
                    self._rrf_k + rank + 1
                )

        _add_ranked(lex_hits)
        _add_ranked(sem_hits)
        if not scores:
            return self._chunks[:k]
        ordered = sorted(scores.items(), key=lambda x: -x[1])
        out: list[TextChunk] = []
        seen: set[int] = set()
        for cid, _ in ordered:
            if cid in seen:
                continue
            seen.add(cid)
            out.append(chunk_by_id[cid])
            if len(out) >= k:
                break
        if len(out) < k:
            for c in self._chunks:
                if len(out) >= k:
                    break
                if id(c) not in seen:
                    out.append(c)
                    seen.add(id(c))
        return out


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


class MultiPoolQuotaRetriever(BaseRetriever):
    """Recupera por cupos en varios pools y completa hasta top_k."""

    def __init__(
        self,
        inner_builder,
        pool_specs: list[tuple[list[TextChunk], int]],
        all_chunks: Sequence[TextChunk],
        default_top_k: int,
    ):
        self._inner_builder = inner_builder
        self._pool_specs = [
            (list(chunks), max(0, quota))
            for chunks, quota in pool_specs
            if chunks and quota > 0
        ]
        self._all_chunks = list(all_chunks)
        self._default_top_k = default_top_k

    def retrieve(self, query: str, top_k: int) -> list[TextChunk]:
        k = top_k if top_k > 0 else self._default_top_k
        picked: list[TextChunk] = []

        for chunks, quota in self._pool_specs:
            inner = self._inner_builder(chunks)
            picked.extend(inner.retrieve(query, quota))

        picked = _dedupe_chunks(picked)
        if len(picked) >= k:
            return picked[:k]

        if picked and self._all_chunks:
            inner_all = self._inner_builder(self._all_chunks)
            extra = inner_all.retrieve(query, k)
            seen = {id(c) for c in picked}
            for c in extra:
                if len(picked) >= k:
                    break
                if id(c) not in seen:
                    picked.append(c)
                    seen.add(id(c))
            return picked

        if not self._all_chunks:
            return []
        return self._inner_builder(self._all_chunks).retrieve(query, k)


class QuotaRetriever(MultiPoolQuotaRetriever):
    """Cupos processed vs pdf (compatibilidad E6/E7)."""

    def __init__(
        self,
        inner_builder,
        processed_chunks: Sequence[TextChunk],
        pdf_chunks: Sequence[TextChunk],
        quota_processed: int,
        quota_pdf: int,
        default_top_k: int,
    ):
        super().__init__(
            inner_builder,
            [
                (list(processed_chunks), quota_processed),
                (list(pdf_chunks), quota_pdf),
            ],
            list(processed_chunks) + list(pdf_chunks),
            default_top_k,
        )


def _build_semantic_retriever(
    settings: Settings, chunks: list[TextChunk], backend: str
) -> BaseRetriever:
    """Rama semántica (http | local) para uso directo o en híbrido."""
    if backend == "http":
        from regatas_assistant.rag.embeddings_http import (
            HttpEmbeddingEncoder,
            embed_corpus_http,
        )

        if not settings.llm_api_key:
            raise ValueError(
                "Embeddings HTTP requieren REGATAS_LLM_API_KEY en el entorno."
            )
        enc = HttpEmbeddingEncoder(settings)
        matrix = embed_corpus_http(enc, [c.text for c in chunks])
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
        f"Rama semántica desconocida: {backend!r}. Use http | local."
    )


def _build_inner_retriever(settings: Settings, chunks: list[TextChunk]) -> BaseRetriever:
    backend = settings.embedding_backend
    if backend == "lexical":
        return LexicalRetriever(chunks)

    if backend == "hybrid":
        sem_backend = settings.hybrid_semantic_backend
        return HybridRetriever(
            chunks,
            LexicalRetriever(chunks),
            _build_semantic_retriever(settings, chunks, sem_backend),
            rrf_k=settings.hybrid_rrf_k,
        )

    if backend in ("http", "local"):
        return _build_semantic_retriever(settings, chunks, backend)

    raise ValueError(
        f"REGATAS_EMBEDDING_BACKEND desconocido: {backend}. "
        "Use lexical | http | local | hybrid."
    )


def build_retriever(settings: Settings, chunks: list[TextChunk]) -> BaseRetriever:
    if not settings.retrieval_use_quotas:
        return _build_inner_retriever(settings, chunks)

    inner_builder = lambda subset: _build_inner_retriever(settings, subset)

    if settings.retrieval_quota_by_doctype:
        pools = split_chunks_by_doctype(chunks)
        quotas = settings.resolve_retrieval_quotas_by_doctype(
            {key: len(pools[key]) for key in pools}
        )
        specs: list[tuple[list[TextChunk], int]] = []
        for key in ("rrs", "call", "case", "definition"):
            if quotas.get(key, 0) > 0 and pools[key]:
                specs.append((pools[key], quotas[key]))
        if pools["pdf"]:
            qpdf = settings.retrieval_quota_pdf
            if qpdf is None and settings.retrieval_quota_processed is not None:
                _, qpdf = settings.resolve_retrieval_quotas(
                    sum(len(pools[k]) for k in ("rrs", "call", "case", "definition")),
                    len(pools["pdf"]),
                )
            if qpdf is None:
                qpdf = 0
            qpdf = min(max(0, qpdf), len(pools["pdf"]), settings.retrieve_top_k)
            if qpdf > 0:
                specs.append((pools["pdf"], qpdf))
        if not specs:
            return _build_inner_retriever(settings, chunks)
        return MultiPoolQuotaRetriever(
            inner_builder,
            specs,
            chunks,
            settings.retrieve_top_k,
        )

    processed, pdf = split_chunks_by_bucket(chunks)
    qp, qpdf = settings.resolve_retrieval_quotas(len(processed), len(pdf))
    if qp <= 0 and qpdf <= 0:
        return _build_inner_retriever(settings, chunks)

    return QuotaRetriever(
        inner_builder,
        processed,
        pdf,
        qp,
        qpdf,
        settings.retrieve_top_k,
    )


class CorpusRetriever:
    """Fachada estable para el pipeline."""

    def __init__(self, inner: BaseRetriever, default_top_k: int):
        self._inner = inner
        self._default_top_k = default_top_k

    def retrieve(self, query: str, top_k: int | None = None) -> list[TextChunk]:
        k = top_k if top_k is not None else self._default_top_k
        return self._inner.retrieve(query, k)
