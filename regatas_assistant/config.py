"""Carga de configuración desde variables de entorno (local, Docker, HF Spaces)."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from regatas_assistant.prompts import normalize_prompt_strategy

# API HTTP de chat/embeddings (p. ej. Ollama, vLLM, hosts con rutas tipo /v1)
DEFAULT_LLM_BASE_URL = "http://127.0.0.1:11434/v1"
DEFAULT_LLM_API_KEY = "ollama"
DEFAULT_LLM_MODEL = "llama3"
DEFAULT_EMBEDDING_API_MODEL = "text-embedding-3-small"

# Subcarpeta bajo `base_dir` donde viven los PDF ingeridos por defecto.
DEFAULT_CORPUS_SUBDIR = "corpus"


def _root_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def _bool(name: str, default: bool = False) -> bool:
    v = os.environ.get(name)
    if v is None:
        return default
    return v.strip().lower() in ("1", "true", "yes", "on")


def _is_huggingface_space() -> bool:
    if os.environ.get("SYSTEM") == "spaces":
        return True
    sid = os.environ.get("SPACE_ID")
    return bool(sid and str(sid).strip())


def _env_strip(name: str) -> str | None:
    v = os.environ.get(name)
    if v is None:
        return None
    return v.strip()


def _env_preferred(primary: str, legacy: str) -> str | None:
    """Valor de entorno: prioriza `primary`, si no existe usa `legacy`."""
    a = _env_strip(primary)
    if a is not None:
        return a
    return _env_strip(legacy)


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
    corpus_subdir: str = DEFAULT_CORPUS_SUBDIR
    # lexical | http | local  (valor legacy `openai` se normaliza a `http` en from_env)
    embedding_backend: str = "lexical"
    llm_api_key: str | None = None
    llm_base_url: str | None = None
    llm_model: str = DEFAULT_LLM_MODEL
    embedding_api_model: str = DEFAULT_EMBEDDING_API_MODEL
    local_embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    # stub | http  (valor legacy `openai` se normaliza a `http` en from_env)
    llm_backend: str = "http"
    # es | en — idioma del system prompt (plantilla); el informe sigue en español por diseño
    system_prompt_language: str = "es"
    # cot | few_shot_cot — plantilla de system prompt (CoT explícito vs Few-Shot CoT con ranura de ejemplos)
    prompt_strategy: str = "cot"
    index_cache_dir: Path | None = None
    llm_timeout_seconds: float = 600.0

    @property
    def corpus_paths(self) -> list[Path]:
        root = self.base_dir / self.corpus_subdir
        return [root / name for name in self.corpus_filenames]

    @classmethod
    def from_env(cls) -> Settings:
        base = Path(os.environ.get("REGATAS_BASE_DIR", _root_dir())).resolve()
        corpus_subdir = (
            _env_strip("REGATAS_CORPUS_SUBDIR") or DEFAULT_CORPUS_SUBDIR
        )
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

        in_space = _is_huggingface_space()

        llm_backend_raw = os.environ.get("REGATAS_LLM_BACKEND")
        if llm_backend_raw is not None and llm_backend_raw.strip():
            raw_lb = llm_backend_raw.strip().lower()
            llm_backend = "http" if raw_lb in ("http", "openai") else raw_lb
        else:
            llm_backend = "stub" if in_space else "http"

        # Fallback de nombres de entorno heredados del ecosistema (mismo significado que REGATAS_*).
        base_url_set = _env_preferred("REGATAS_LLM_BASE_URL", "OPENAI_BASE_URL")
        if base_url_set is not None:
            llm_base_url = base_url_set or None
        elif in_space:
            llm_base_url = None
        else:
            llm_base_url = DEFAULT_LLM_BASE_URL

        key_set = _env_preferred("REGATAS_LLM_API_KEY", "OPENAI_API_KEY")
        if key_set is not None and key_set:
            llm_api_key = key_set
        elif in_space:
            llm_api_key = None
        else:
            llm_api_key = DEFAULT_LLM_API_KEY

        model_set = _env_preferred("REGATAS_LLM_MODEL", "OPENAI_LLM_MODEL")
        if model_set:
            llm_model = model_set
        elif in_space:
            llm_model = "gpt-4o-mini"
        else:
            llm_model = DEFAULT_LLM_MODEL

        emb = _env_preferred("REGATAS_EMBEDDING_MODEL", "OPENAI_EMBEDDING_MODEL")
        embedding_api_model = emb if emb else DEFAULT_EMBEDDING_API_MODEL

        spl_raw = os.environ.get("REGATAS_SYSTEM_PROMPT_LANG", "es").strip().lower()
        system_prompt_language = (
            "en"
            if spl_raw in ("en", "english", "ingles", "inglés")
            else "es"
        )

        strat_raw = os.environ.get("REGATAS_PROMPT_STRATEGY", "cot")
        prompt_strategy = normalize_prompt_strategy(strat_raw)

        emb_b_raw = os.environ.get("REGATAS_EMBEDDING_BACKEND", "lexical").strip().lower()
        if emb_b_raw in ("http", "openai"):
            embedding_backend = "http"
        elif emb_b_raw == "local":
            embedding_backend = "local"
        else:
            embedding_backend = "lexical"

        try:
            llm_timeout_seconds = float(
                os.environ.get("REGATAS_LLM_TIMEOUT", "600")
            )
        except ValueError:
            llm_timeout_seconds = 600.0
        if llm_timeout_seconds <= 0:
            llm_timeout_seconds = 600.0

        return cls(
            base_dir=base,
            corpus_subdir=corpus_subdir,
            corpus_filenames=corpus_filenames,
            chunk_size=int(os.environ.get("REGATAS_CHUNK_SIZE", "900")),
            chunk_overlap=int(os.environ.get("REGATAS_CHUNK_OVERLAP", "120")),
            retrieve_top_k=int(os.environ.get("REGATAS_TOP_K", "8")),
            embedding_backend=embedding_backend,
            llm_api_key=llm_api_key,
            llm_base_url=llm_base_url,
            llm_model=llm_model,
            embedding_api_model=embedding_api_model,
            local_embedding_model=os.environ.get(
                "REGATAS_LOCAL_EMBEDDING_MODEL",
                "sentence-transformers/all-MiniLM-L6-v2",
            ),
            llm_backend=llm_backend,
            system_prompt_language=system_prompt_language,
            prompt_strategy=prompt_strategy,
            index_cache_dir=index_cache_dir,
            llm_timeout_seconds=llm_timeout_seconds,
        )


def is_huggingface_space() -> bool:
    """True en Hugging Face Spaces (`SPACE_ID` o `SYSTEM=spaces`)."""
    return _is_huggingface_space()
