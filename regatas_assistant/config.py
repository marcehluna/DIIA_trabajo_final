"""Carga de configuración desde variables de entorno (local, Docker, HF Spaces)."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from regatas_assistant.prompts import normalize_prompt_strategy, normalize_response_language

# API HTTP de chat/embeddings (p. ej. Ollama, vLLM, hosts con rutas tipo /v1)
DEFAULT_LLM_BASE_URL = "http://127.0.0.1:11434/v1"
DEFAULT_LLM_API_KEY = "ollama"
DEFAULT_LLM_MODEL = "llama3"
DEFAULT_EMBEDDING_API_MODEL = "text-embedding-3-small"

# Subcarpeta bajo `base_dir` donde viven los PDF ingeridos por defecto.
DEFAULT_CORPUS_SUBDIR = "corpus"

# processed = solo JSONL (RRS + definiciones desde CSV)
# pdf = solo PDFs listados en corpus_filenames
# full = JSONL + PDFs (comportamiento mixto anterior)
CORPUS_SOURCES_PROCESSED = "processed"
CORPUS_SOURCES_PDF = "pdf"
CORPUS_SOURCES_FULL = "full"
# Por defecto en código: perfil producción (E11). Override: REGATAS_PROFILE=baseline|legacy
DEFAULT_CORPUS_SOURCES = CORPUS_SOURCES_PROCESSED


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
    # lexical | http | local | hybrid (léxico + semántica, RRF)
    embedding_backend: str = "lexical"
    # Rama semántica cuando embedding_backend=hybrid
    hybrid_semantic_backend: str = "local"
    hybrid_rrf_k: int = 60
    llm_api_key: str | None = None
    llm_base_url: str | None = None
    llm_model: str = DEFAULT_LLM_MODEL
    embedding_api_model: str = DEFAULT_EMBEDDING_API_MODEL
    local_embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    # stub | http  (valor legacy `openai` se normaliza a `http` en from_env)
    llm_backend: str = "http"
    # es | en — idioma del system prompt (plantilla legacy); ver response_language para el informe
    system_prompt_language: str = "es"
    # es | en — idioma del informe generado (en = E14, corpus alineado)
    response_language: str = "es"
    # cot | few_shot_cot — plantilla de system prompt (CoT explícito vs Few-Shot CoT con ranura de ejemplos)
    prompt_strategy: str = "cot"
    index_cache_dir: Path | None = None
    llm_timeout_seconds: float = 600.0
    # Cargar corpus/processed/*.jsonl (RRS y definiciones desde CSV)
    load_processed_jsonl: bool = True
    # Qué fuentes entran al índice RAG (ver REGATAS_CORPUS_SOURCES)
    corpus_sources: str = DEFAULT_CORPUS_SOURCES
    # Perfil activo (production | baseline | legacy); ver regatas_assistant/profiles.py
    active_profile: str = "production"
    # Cupos de retrieval: processed (RRS JSONL) vs pdf (Call/Case)
    retrieval_use_quotas: bool = True
    retrieval_quota_processed: int | None = None
    retrieval_quota_pdf: int | None = None
    # Cupos por doc_type (rrs, call, case, definition) — producción E11: 2+3+2+1
    retrieval_quota_by_doctype: bool = True
    retrieval_quota_rrs: int | None = 2
    retrieval_quota_call: int | None = 3
    retrieval_quota_case: int | None = 2
    retrieval_quota_definition: int | None = 1

    @property
    def corpus_paths(self) -> list[Path]:
        root = self.base_dir / self.corpus_subdir
        return [root / name for name in self.corpus_filenames]

    @property
    def corpus_processed_dir(self) -> Path:
        return self.base_dir / self.corpus_subdir / "processed"

    def resolve_retrieval_quotas(
        self, n_processed: int, n_pdf: int
    ) -> tuple[int, int]:
        """Cupos por pool; None = reparto automático de retrieve_top_k."""
        k = self.retrieve_top_k
        if n_processed <= 0 and n_pdf <= 0:
            return 0, 0
        if n_processed <= 0:
            return 0, min(k, n_pdf)
        if n_pdf <= 0:
            return min(k, n_processed), 0

        qp = self.retrieval_quota_processed
        qpdf = self.retrieval_quota_pdf
        if qp is None and qpdf is None:
            qp = k // 2
            qpdf = k - qp
        elif qp is None:
            qp = max(0, k - (qpdf or 0))
        elif qpdf is None:
            qpdf = max(0, k - qp)

        qp = min(max(0, qp), n_processed, k)
        qpdf = min(max(0, qpdf), n_pdf, k)
        if qp + qpdf > k:
            overflow = qp + qpdf - k
            cut_pdf = min(overflow, qpdf)
            qpdf -= cut_pdf
            qp -= overflow - cut_pdf
        return qp, qpdf

    def resolve_retrieval_quotas_by_doctype(
        self, counts: dict[str, int]
    ) -> dict[str, int]:
        """Cupos por doc_type; None = defaults 3+2+2+1 para top_k=8."""
        k = self.retrieve_top_k
        keys = ("rrs", "call", "case", "definition")
        explicit = {
            "rrs": self.retrieval_quota_rrs,
            "call": self.retrieval_quota_call,
            "case": self.retrieval_quota_case,
            "definition": self.retrieval_quota_definition,
        }
        defaults = {"rrs": 3, "call": 2, "case": 2, "definition": 1}
        if all(explicit[k] is None for k in keys):
            base = dict(defaults)
        else:
            base = {key: explicit[key] or 0 for key in keys}

        out: dict[str, int] = {}
        total = 0
        for key in keys:
            n = counts.get(key, 0)
            q = min(max(0, base[key]), n, k)
            out[key] = q
            total += q
        if total > k:
            overflow = total - k
            for key in ("definition", "case", "call", "rrs"):
                cut = min(overflow, out[key])
                out[key] -= cut
                overflow -= cut
                if overflow <= 0:
                    break
        return out

    @classmethod
    def from_env(cls) -> Settings:
        from regatas_assistant.profiles import normalize_profile, profile_defaults

        profile = normalize_profile(_env_strip("REGATAS_PROFILE"))
        prof = profile_defaults(profile)

        base = Path(os.environ.get("REGATAS_BASE_DIR", _root_dir())).resolve()
        corpus_subdir = (
            _env_strip("REGATAS_CORPUS_SUBDIR") or DEFAULT_CORPUS_SUBDIR
        )
        corpus_filenames: tuple[str, ...]
        if "REGATAS_CORPUS_FILES" in os.environ:
            raw = os.environ.get("REGATAS_CORPUS_FILES", "")
            corpus_filenames = tuple(
                f.strip() for f in raw.split(",") if f.strip()
            )
        else:
            corpus_filenames = prof["corpus_filenames"]
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

        response_language = normalize_response_language(
            os.environ.get("REGATAS_RESPONSE_LANG", "es")
        )

        emb_b_raw = os.environ.get("REGATAS_EMBEDDING_BACKEND", "lexical").strip().lower()
        if emb_b_raw in ("http", "openai"):
            embedding_backend = "http"
        elif emb_b_raw == "local":
            embedding_backend = "local"
        elif emb_b_raw == "hybrid":
            embedding_backend = "hybrid"
        else:
            embedding_backend = "lexical"

        hybrid_sem_raw = (
            _env_strip("REGATAS_HYBRID_SEMANTIC_BACKEND") or "local"
        ).lower()
        hybrid_semantic_backend = (
            "http" if hybrid_sem_raw in ("http", "openai") else "local"
        )
        try:
            hybrid_rrf_k = int(os.environ.get("REGATAS_HYBRID_RRF_K", "60"))
        except ValueError:
            hybrid_rrf_k = 60
        if hybrid_rrf_k < 1:
            hybrid_rrf_k = 60

        try:
            llm_timeout_seconds = float(
                os.environ.get("REGATAS_LLM_TIMEOUT", "600")
            )
        except ValueError:
            llm_timeout_seconds = 600.0
        if llm_timeout_seconds <= 0:
            llm_timeout_seconds = 600.0

        if "REGATAS_LOAD_PROCESSED" in os.environ:
            load_processed_jsonl = _bool("REGATAS_LOAD_PROCESSED", default=True)
        else:
            load_processed_jsonl = prof["load_processed_jsonl"]

        if _env_strip("REGATAS_CORPUS_SOURCES"):
            src_raw = _env_strip("REGATAS_CORPUS_SOURCES").lower()
            if src_raw in ("processed", "rrs", "jsonl", "csv"):
                corpus_sources = CORPUS_SOURCES_PROCESSED
            elif src_raw in ("pdf", "pdfs"):
                corpus_sources = CORPUS_SOURCES_PDF
            elif src_raw in ("full", "mixed", "all"):
                corpus_sources = CORPUS_SOURCES_FULL
            else:
                corpus_sources = prof["corpus_sources"]
        else:
            corpus_sources = prof["corpus_sources"]

        if corpus_sources == CORPUS_SOURCES_PROCESSED:
            load_processed_jsonl = True

        if "REGATAS_RETRIEVAL_QUOTAS" in os.environ:
            retrieval_use_quotas = _bool("REGATAS_RETRIEVAL_QUOTAS", default=False)
        else:
            retrieval_use_quotas = prof["retrieval_use_quotas"]

        def _quota_int(name: str, prof_key: str) -> int | None:
            raw = _env_strip(name)
            if raw:
                return int(raw)
            return prof.get(prof_key)

        qp_raw = _env_strip("REGATAS_RETRIEVAL_QUOTA_PROCESSED")
        qpdf_raw = _env_strip("REGATAS_RETRIEVAL_QUOTA_PDF")
        retrieval_quota_processed = int(qp_raw) if qp_raw else prof["retrieval_quota_processed"]
        retrieval_quota_pdf = int(qpdf_raw) if qpdf_raw else prof["retrieval_quota_pdf"]

        retrieval_quota_rrs = _quota_int(
            "REGATAS_RETRIEVAL_QUOTA_RRS", "retrieval_quota_rrs"
        )
        retrieval_quota_call = _quota_int(
            "REGATAS_RETRIEVAL_QUOTA_CALL", "retrieval_quota_call"
        )
        retrieval_quota_case = _quota_int(
            "REGATAS_RETRIEVAL_QUOTA_CASE", "retrieval_quota_case"
        )
        retrieval_quota_definition = _quota_int(
            "REGATAS_RETRIEVAL_QUOTA_DEFINITION", "retrieval_quota_definition"
        )

        if "REGATAS_RETRIEVAL_QUOTA_BY_DOCTYPE" in os.environ:
            retrieval_quota_by_doctype = _bool(
                "REGATAS_RETRIEVAL_QUOTA_BY_DOCTYPE", default=False
            )
        else:
            retrieval_quota_by_doctype = prof["retrieval_quota_by_doctype"]
        if any(
            x is not None
            for x in (
                retrieval_quota_rrs,
                retrieval_quota_call,
                retrieval_quota_case,
                retrieval_quota_definition,
            )
        ):
            retrieval_quota_by_doctype = True

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
            response_language=response_language,
            prompt_strategy=prompt_strategy,
            index_cache_dir=index_cache_dir,
            llm_timeout_seconds=llm_timeout_seconds,
            load_processed_jsonl=load_processed_jsonl,
            corpus_sources=corpus_sources,
            retrieval_use_quotas=retrieval_use_quotas,
            retrieval_quota_processed=retrieval_quota_processed,
            retrieval_quota_pdf=retrieval_quota_pdf,
            retrieval_quota_by_doctype=retrieval_quota_by_doctype,
            retrieval_quota_rrs=retrieval_quota_rrs,
            retrieval_quota_call=retrieval_quota_call,
            retrieval_quota_case=retrieval_quota_case,
            retrieval_quota_definition=retrieval_quota_definition,
            active_profile=profile,
            hybrid_semantic_backend=hybrid_semantic_backend,
            hybrid_rrf_k=hybrid_rrf_k,
        )


def is_huggingface_space() -> bool:
    """True en Hugging Face Spaces (`SPACE_ID` o `SYSTEM=spaces`)."""
    return _is_huggingface_space()
