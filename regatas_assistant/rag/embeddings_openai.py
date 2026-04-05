"""Embeddings vía API compatible con OpenAI."""

from __future__ import annotations

import numpy as np

from regatas_assistant.config import Settings


class OpenAIEmbeddingEncoder:
    def __init__(self, settings: Settings):
        from openai import OpenAI

        self._client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url or None,
        )
        self._model = settings.openai_embedding_model

    def embed_one(self, text: str) -> list[float]:
        r = self._client.embeddings.create(model=self._model, input=text[:8000])
        return list(r.data[0].embedding)

    def embed_batch(self, texts: list[str], batch_size: int = 64) -> list[list[float]]:
        out: list[list[float]] = []
        for i in range(0, len(texts), batch_size):
            batch = [t[:8000] for t in texts[i : i + batch_size]]
            r = self._client.embeddings.create(model=self._model, input=batch)
            by_idx = sorted(r.data, key=lambda d: d.index)
            out.extend(list(d.embedding) for d in by_idx)
        return out


def embed_corpus_openai(encoder: OpenAIEmbeddingEncoder, texts: list[str]) -> np.ndarray:
    vecs = encoder.embed_batch(texts)
    return np.array(vecs, dtype=np.float32)
