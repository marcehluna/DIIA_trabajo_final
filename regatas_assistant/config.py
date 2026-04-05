"""Carga de configuración desde variables de entorno (local, Docker, HF Spaces)."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _root_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def _bool(name: str, default: bool = False) -> bool:
    v = os.environ.get(name)
    if v is None:
        return default
    return v.strip().lower() in ("1", "true", "yes", "on")


@dataclass
class Settings:
    """Parámetros de la PoC; todos sobreescribibles por entorno."""

    base_dir: Path = field(default_factory=_root_dir)
    corpus_filenames: tuple[str, ...] = (
        "The-Call-Book-for-Team-Racing-2025-2028.pdf",
        "WS-Case-Book-2025-2028-v2025-07.pdf",
    )
    chunk_size: int = 900
    chunk_overlap: int = 120
    retrieve_top_k: int = 8
    # lexical | openai | local
    embedding_backend: str = "lexical"
    openai_api_key: str | None = None
    openai_base_url: str | None = None
    openai_llm_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    local_embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    # stub | openai
    llm_backend: str = "stub"
    index_cache_dir: Path | None = None

    @property
    def corpus_paths(self) -> list[Path]:
        return [self.base_dir / name for name in self.corpus_filenames]

    @classmethod
    def from_env(cls) -> Settings:
        base = Path(os.environ.get("REGATAS_BASE_DIR", _root_dir())).resolve()
        files = os.environ.get("REGATAS_CORPUS_FILES")
        corpus_filenames: tuple[str, ...]
        if files:
            corpus_filenames = tuple(f.strip() for f in files.split(",") if f.strip())
        else:
            corpus_filenames = (
                "The-Call-Book-for-Team-Racing-2025-2028.pdf",
                "WS-Case-Book-2025-2028-v2025-07.pdf",
            )
        cache_raw = os.environ.get("REGATAS_INDEX_CACHE_DIR")
        index_cache_dir = Path(cache_raw).resolve() if cache_raw else None

        return cls(
            base_dir=base,
            corpus_filenames=corpus_filenames,
            chunk_size=int(os.environ.get("REGATAS_CHUNK_SIZE", "900")),
            chunk_overlap=int(os.environ.get("REGATAS_CHUNK_OVERLAP", "120")),
            retrieve_top_k=int(os.environ.get("REGATAS_TOP_K", "8")),
            embedding_backend=os.environ.get(
                "REGATAS_EMBEDDING_BACKEND", "lexical"
            ).lower(),
            openai_api_key=os.environ.get("OPENAI_API_KEY"),
            openai_base_url=os.environ.get("OPENAI_BASE_URL"),
            openai_llm_model=os.environ.get("OPENAI_LLM_MODEL", "gpt-4o-mini"),
            openai_embedding_model=os.environ.get(
                "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
            ),
            local_embedding_model=os.environ.get(
                "REGATAS_LOCAL_EMBEDDING_MODEL",
                "sentence-transformers/all-MiniLM-L6-v2",
            ),
            llm_backend=os.environ.get("REGATAS_LLM_BACKEND", "stub").lower(),
            index_cache_dir=index_cache_dir,
        )


def is_huggingface_space() -> bool:
    return _bool("SPACE_ID") or os.environ.get("SYSTEM") == "spaces"
