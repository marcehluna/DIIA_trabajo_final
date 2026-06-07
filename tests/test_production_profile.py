"""Regresión de configuración: perfil productivo E11 (retrieval) + E13 (respuesta)."""

from __future__ import annotations

import os
import unittest
from contextlib import contextmanager

from regatas_assistant.config import CORPUS_SOURCES_PROCESSED, Settings
from regatas_assistant.profiles import (
    PROFILE_PRODUCTION,
    RETRIEVAL_REFERENCE_RUN_ID,
    RESPONSE_REFERENCE_RUN_ID,
    profile_defaults,
)

_REGATAS_PREFIX = "REGATAS_"
_HF_KEYS = frozenset({"SPACE_ID", "SYSTEM", "OPENAI_BASE_URL", "OPENAI_API_KEY"})


@contextmanager
def _isolated_regatas_env(*, extra: dict[str, str | None] | None = None):
    """Quita overrides REGATAS_* (y HF) para probar defaults de producción."""
    saved = os.environ.copy()
    try:
        for key in list(os.environ):
            if key.startswith(_REGATAS_PREFIX) or key in _HF_KEYS:
                del os.environ[key]
        if extra:
            for k, v in extra.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
        yield
    finally:
        os.environ.clear()
        os.environ.update(saved)


class ProductionProfileDefaultsTest(unittest.TestCase):
    def test_settings_from_env_without_overrides(self):
        with _isolated_regatas_env():
            s = Settings.from_env()

        self.assertEqual(s.active_profile, PROFILE_PRODUCTION)
        self.assertEqual(s.embedding_backend, "lexical")
        self.assertEqual(s.response_language, "es")
        self.assertEqual(s.system_prompt_language, "es")
        self.assertEqual(s.prompt_strategy, "cot")
        self.assertEqual(s.corpus_sources, CORPUS_SOURCES_PROCESSED)
        self.assertTrue(s.load_processed_jsonl)
        self.assertEqual(s.corpus_filenames, ())
        self.assertTrue(s.retrieval_use_quotas)
        self.assertTrue(s.retrieval_quota_by_doctype)
        self.assertEqual(s.retrieval_quota_rrs, 2)
        self.assertEqual(s.retrieval_quota_call, 3)
        self.assertEqual(s.retrieval_quota_case, 2)
        self.assertEqual(s.retrieval_quota_definition, 1)

    def test_production_profile_never_defaults_to_hybrid(self):
        with _isolated_regatas_env():
            s = Settings.from_env()

        self.assertNotEqual(s.embedding_backend, "hybrid")

    def test_profile_defaults_match_e11_retrieval(self):
        prof = profile_defaults(PROFILE_PRODUCTION)

        self.assertEqual(prof["corpus_sources"], CORPUS_SOURCES_PROCESSED)
        self.assertTrue(prof["load_processed_jsonl"])
        self.assertTrue(prof["retrieval_use_quotas"])
        self.assertTrue(prof["retrieval_quota_by_doctype"])
        self.assertEqual(prof["retrieval_quota_rrs"], 2)
        self.assertEqual(prof["retrieval_quota_call"], 3)
        self.assertEqual(prof["retrieval_quota_case"], 2)
        self.assertEqual(prof["retrieval_quota_definition"], 1)

    def test_reference_run_ids_document_e11_e13(self):
        self.assertIn("processed_cupos_2_3_2_1", RETRIEVAL_REFERENCE_RUN_ID)
        self.assertIn("prompt_v3", RESPONSE_REFERENCE_RUN_ID)


if __name__ == "__main__":
    unittest.main()
