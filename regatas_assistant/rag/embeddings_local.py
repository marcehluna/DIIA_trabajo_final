"""Embeddings locales con sentence-transformers (CPU/GPU según entorno)."""

from __future__ import annotations

import numpy as np


class LocalSentenceEncoder:
    def __init__(self, model_id: str):
        from sentence_transformers import SentenceTransformer

        self._model = SentenceTransformer(model_id)

    def encode_corpus(self, texts: list[str], batch_size: int = 32) -> np.ndarray:
        emb = self._model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=len(texts) > 200,
            convert_to_numpy=True,
        )
        return np.asarray(emb, dtype=np.float32)

    def encode_query(self, text: str) -> list[float]:
        v = self._model.encode([text], convert_to_numpy=True)[0]
        return np.asarray(v, dtype=np.float32).tolist()


def embed_corpus_local(encoder: LocalSentenceEncoder, texts: list[str]) -> np.ndarray:
    return encoder.encode_corpus(texts)
