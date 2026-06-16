#!/usr/bin/env python3
"""Verifica corpus RAG, configuración y conectividad con Ollama antes de usar la app."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from regatas_assistant.config import Settings
from regatas_assistant.ingestion import corpus_chunk_summary, load_corpus_chunks
from regatas_assistant.ollama_models import (
    list_installed_ollama_models,
    resolve_model_name,
)
from regatas_assistant.rag.retriever import build_retriever


def _ok(msg: str) -> None:
    print(f"  OK  {msg}")


def _fail(msg: str) -> None:
    print(f"  FAIL {msg}")


def _warn(msg: str) -> None:
    print(f"  WARN {msg}")


def check_config(s: Settings) -> list[str]:
    errors: list[str] = []
    print("\n[1] Configuración (Settings.from_env)")
    print(f"      perfil={s.active_profile} corpus_sources={s.corpus_sources}")
    print(f"      embedding={s.embedding_backend} top_k={s.retrieve_top_k}")
    print(f"      llm_backend={s.llm_backend} model={s.llm_model}")
    print(f"      llm_base_url={s.llm_base_url}")
    print(f"      quotas by_doctype={s.retrieval_quota_by_doctype}")

    if s.llm_backend == "http" and not s.llm_api_key:
        errors.append("REGATAS_LLM_API_KEY vacío con backend http")
        _fail("REGATAS_LLM_API_KEY requerido para backend http")
    else:
        _ok("LLM backend y credenciales básicas")

    processed_dir = s.corpus_processed_dir
    if s.corpus_sources == "processed" and not processed_dir.is_dir():
        errors.append(f"Falta {processed_dir}")
        _fail(f"Directorio processed no existe: {processed_dir}")
    else:
        _ok(f"Corpus processed: {processed_dir}")

    return errors


def check_corpus(s: Settings) -> tuple[list[str], list]:
    errors: list[str] = []
    print("\n[2] Corpus e índice RAG")
    t0 = time.time()
    try:
        chunks = load_corpus_chunks(s)
    except (FileNotFoundError, ValueError) as exc:
        errors.append(str(exc))
        _fail(str(exc))
        return errors, []
    elapsed = time.time() - t0
    summary = corpus_chunk_summary(chunks)
    _ok(f"{summary['total']} chunks en {elapsed:.2f}s — {summary}")

    t1 = time.time()
    retriever = build_retriever(s, chunks)
    _ok(f"Índice construido en {time.time() - t1:.2f}s")

    t2 = time.time()
    hits = retriever.retrieve("barco orzó en ceñida contacto amura", s.retrieve_top_k)
    _ok(
        f"Retrieval de prueba: {len(hits)} fragmentos en {time.time() - t2:.2f}s"
    )
    for h in hits[:3]:
        print(f"        · {h.header_line()[:90]}")
    if len(hits) < 1:
        errors.append("Retrieval devolvió 0 fragmentos")
        _fail("Retrieval vacío")
    return errors, chunks


def check_ollama(s: Settings) -> list[str]:
    errors: list[str] = []
    print("\n[3] Ollama / API HTTP del LLM")
    if s.llm_backend != "http":
        _warn(f"llm_backend={s.llm_backend!r} — omitiendo prueba de Ollama")
        return errors

    installed = list_installed_ollama_models(s.llm_base_url)
    if not installed:
        msg = (
            "No se pudo leer /api/tags. ¿Ollama en marcha? "
            f"URL base: {s.llm_base_url}"
        )
        errors.append(msg)
        _fail(msg)
        return errors

    _ok(f"Modelos instalados: {', '.join(installed)}")
    resolved = resolve_model_name(installed, s.llm_model)
    if resolved != s.llm_model:
        _warn(f"REGATAS_LLM_MODEL={s.llm_model!r} → resuelto a {resolved!r}")
    elif resolved not in installed:
        errors.append(f"Modelo {s.llm_model!r} no está en Ollama")
        _fail(f"Modelo configurado no instalado: {s.llm_model!r}")
        return errors
    else:
        _ok(f"Modelo activo: {resolved}")

    from regatas_assistant.llm.chat_http_client import HTTPChatClient

    try:
        client = HTTPChatClient(s)
    except ValueError as exc:
        errors.append(str(exc))
        _fail(str(exc))
        return errors

    t0 = time.time()
    try:
        reply = client.complete(
            "You are a test assistant.",
            "Responde solo con la palabra LISTO.",
            model=resolved,
        )
    except Exception as exc:
        errors.append(f"LLM HTTP: {exc!r}")
        _fail(f"Llamada chat/completions: {exc!r}")
        return errors

    elapsed = time.time() - t0
    preview = (reply or "").strip().replace("\n", " ")[:80]
    _ok(f"Respuesta en {elapsed:.1f}s: {preview!r}")
    if elapsed > 120:
        _warn(
            "La respuesta tardó >2 min; en la app el informe completo puede tardar varios minutos."
        )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Verifica RAG + Ollama + config.")
    parser.add_argument(
        "--skip-llm",
        action="store_true",
        help="Omitir llamada de prueba al LLM (solo corpus y Ollama tags).",
    )
    args = parser.parse_args()

    print("Regatas assistant — check_setup")
    print(f"ROOT={ROOT}")

    s = Settings.from_env()
    all_errors: list[str] = []
    all_errors.extend(check_config(s))
    corpus_errors, _ = check_corpus(s)
    all_errors.extend(corpus_errors)

    if not args.skip_llm:
        all_errors.extend(check_ollama(s))

    print("\n" + "=" * 52)
    if all_errors:
        print("RESULTADO: FALLOS detectados")
        for e in all_errors:
            print(f"  - {e}")
        print("\nSugerencias:")
        print("  · Ollama: ollama serve  (o abrir la app Ollama)")
        print("  · Modelo: ollama pull qwen3:4b")
        print("  · Config: copiar .env.example → .env y ajustar REGATAS_LLM_MODEL")
        return 1

    print("RESULTADO: TODO OK — podés ejecutar ./run.sh o python app.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
