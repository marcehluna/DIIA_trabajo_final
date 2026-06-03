#!/usr/bin/env python3
"""Regenera JSONL desde CSV y muestra el índice RAG solo-RRS (sin Call/Case)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from regatas_assistant.config import CORPUS_SOURCES_PROCESSED, Settings  # noqa: E402
from regatas_assistant.corpus_processed import build_processed_corpus  # noqa: E402
from regatas_assistant.ingestion import corpus_chunk_summary, load_corpus_chunks  # noqa: E402


def main() -> None:
    print("1. Generando corpus/processed/*.jsonl desde CSV…")
    stats = build_processed_corpus(ROOT)
    print(f"   RRS: {stats['rrs_rules']} | Definiciones: {stats.get('definitions', 0)}")

    os.environ["REGATAS_CORPUS_SOURCES"] = CORPUS_SOURCES_PROCESSED
    os.environ["REGATAS_LOAD_PROCESSED"] = "1"
    os.environ["REGATAS_CORPUS_FILES"] = ""

    settings = Settings.from_env()
    assert settings.corpus_sources == CORPUS_SOURCES_PROCESSED

    print("2. Cargando índice (solo processed, sin PDFs)…")
    chunks = load_corpus_chunks(settings)
    summary = corpus_chunk_summary(chunks)

    print("3. Resumen del índice RAG:")
    for key in ("rrs", "definition", "pdf", "total"):
        if key in summary:
            print(f"   {key}: {summary[key]}")
    print()
    print("Para usar este índice en la app o en eval:")
    print("  export REGATAS_CORPUS_SOURCES=processed")
    print("  export REGATAS_CORPUS_FILES=")
    print("  python app.py   # o scripts/eval_run.py …")


if __name__ == "__main__":
    main()
