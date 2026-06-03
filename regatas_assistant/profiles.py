"""Perfiles de configuración RAG (producción, baseline, legacy)."""

from __future__ import annotations

from typing import Any

from regatas_assistant.config import (
    CORPUS_SOURCES_FULL,
    CORPUS_SOURCES_PDF,
    CORPUS_SOURCES_PROCESSED,
)

PROFILE_PRODUCTION = "production"
PROFILE_BASELINE = "baseline"
PROFILE_LEGACY = "legacy"

# Umbrales de regresión vs corrida E11 (eval).
E11_REFERENCE_RUN_ID = "20260526_185624_processed_cupos_2_3_2_1"
E11_REGRESSION_THRESHOLDS: dict[str, float] = {
    "mean_recall_at_k_rules": 0.70,
    "mean_recall_at_k_calls": 0.18,
    "mean_citation_f1_rrs": 0.18,
}


def normalize_profile(name: str | None) -> str:
    if not name:
        return PROFILE_PRODUCTION
    p = name.strip().lower()
    if p in ("production", "prod", "e11", "default"):
        return PROFILE_PRODUCTION
    if p in ("baseline", "e0"):
        return PROFILE_BASELINE
    if p in ("legacy", "full", "mixed"):
        return PROFILE_LEGACY
    return PROFILE_PRODUCTION


def profile_defaults(profile: str) -> dict[str, Any]:
    """Valores por perfil cuando no hay override explícito en el entorno."""
    p = normalize_profile(profile)
    if p == PROFILE_BASELINE:
        return {
            "corpus_sources": CORPUS_SOURCES_PDF,
            "corpus_filenames": (
                "The-Call-Book-for-Team-Racing-2025-2028.pdf",
                "WS-Case-Book-2025-2028-v2025-07.pdf",
            ),
            "load_processed_jsonl": False,
            "retrieval_use_quotas": False,
            "retrieval_quota_by_doctype": False,
            "retrieval_quota_rrs": None,
            "retrieval_quota_call": None,
            "retrieval_quota_case": None,
            "retrieval_quota_definition": None,
            "retrieval_quota_processed": None,
            "retrieval_quota_pdf": None,
        }
    if p == PROFILE_LEGACY:
        return {
            "corpus_sources": CORPUS_SOURCES_FULL,
            "corpus_filenames": (
                "The-Call-Book-for-Team-Racing-2025-2028.pdf",
                "WS-Case-Book-2025-2028-v2025-07.pdf",
            ),
            "load_processed_jsonl": True,
            "retrieval_use_quotas": False,
            "retrieval_quota_by_doctype": False,
            "retrieval_quota_rrs": None,
            "retrieval_quota_call": None,
            "retrieval_quota_case": None,
            "retrieval_quota_definition": None,
            "retrieval_quota_processed": None,
            "retrieval_quota_pdf": None,
        }
    # production (E11)
    return {
        "corpus_sources": CORPUS_SOURCES_PROCESSED,
        "corpus_filenames": (),
        "load_processed_jsonl": True,
        "retrieval_use_quotas": True,
        "retrieval_quota_by_doctype": True,
        "retrieval_quota_rrs": 2,
        "retrieval_quota_call": 3,
        "retrieval_quota_case": 2,
        "retrieval_quota_definition": 1,
        "retrieval_quota_processed": None,
        "retrieval_quota_pdf": None,
    }
