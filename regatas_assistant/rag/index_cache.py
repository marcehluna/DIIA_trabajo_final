"""Caché en disco del índice RAG (vocabulario léxico y matriz semántica)."""

from __future__ import annotations

import hashlib
import pickle
from pathlib import Path

import numpy as np

from regatas_assistant.config import Settings


def default_cache_dir(settings: Settings) -> Path:
    if settings.index_cache_dir is not None:
        return settings.index_cache_dir
    return settings.base_dir / ".cache" / "regatas_index"


def build_fingerprint(settings: Settings, num_chunks: int) -> str:
    manifest_path = settings.corpus_processed_dir / "MANIFEST.json"
    manifest_blob = ""
    if manifest_path.is_file():
        manifest_blob = manifest_path.read_text(encoding="utf-8")
    key_parts = [
        settings.active_profile,
        settings.corpus_sources,
        settings.embedding_backend,
        settings.hybrid_semantic_backend,
        settings.local_embedding_model,
        settings.embedding_api_model,
        str(settings.chunk_size),
        str(settings.chunk_overlap),
        str(num_chunks),
        manifest_blob,
        ",".join(settings.corpus_filenames),
        "1" if settings.load_processed_jsonl else "0",
    ]
    digest = hashlib.sha256("\n".join(key_parts).encode("utf-8")).hexdigest()
    return digest[:20]


class IndexCache:
    def __init__(self, settings: Settings, fingerprint: str):
        self._dir = default_cache_dir(settings)
        self._dir.mkdir(parents=True, exist_ok=True)
        self._stem = self._dir / fingerprint

    @property
    def lexical_path(self) -> Path:
        return Path(f"{self._stem}.lexical.pkl")

    @property
    def semantic_matrix_path(self) -> Path:
        return Path(f"{self._stem}.semantic.npy")

    def load_lexical_vocab(self) -> list[set[str]] | None:
        path = self.lexical_path
        if not path.is_file():
            return None
        try:
            with path.open("rb") as f:
                raw = pickle.load(f)
            if not isinstance(raw, list) or not raw:
                return None
            return [set(item) for item in raw]
        except (OSError, pickle.PickleError, TypeError, ValueError):
            return None

    def save_lexical_vocab(self, vocab: list[set[str]]) -> None:
        path = self.lexical_path
        with path.open("wb") as f:
            pickle.dump([frozenset(v) for v in vocab], f, protocol=pickle.HIGHEST_PROTOCOL)

    def load_semantic_matrix(self) -> np.ndarray | None:
        path = self.semantic_matrix_path
        if not path.is_file():
            return None
        try:
            matrix = np.load(path)
            if matrix.ndim != 2:
                return None
            return np.asarray(matrix, dtype=np.float32)
        except OSError, ValueError:
            return None

    def save_semantic_matrix(self, matrix: np.ndarray) -> None:
        np.save(self.semantic_matrix_path, np.asarray(matrix, dtype=np.float32))
