"""Ejecución de una corrida de evaluación y persistencia de resultados."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from regatas_assistant.config import Settings
from regatas_assistant.eval.golden import load_eval_set
from regatas_assistant.eval.enrich import enrich_report, export_sidecars
from regatas_assistant.eval.metrics import aggregate_metrics, score_case
from regatas_assistant.pipeline import ProtestPipeline


@dataclass
class EvalRunConfig:
    label: str
    retrieval_only: bool = False
    compute_faithfulness: bool = False
    faithfulness_model: str | None = None
    eval_set_path: Path | None = None
    runs_dir: Path | None = None
    system_prompt_lang: str | None = None
    response_language: str | None = None
    prompt_strategy: str | None = None
    llm_model: str | None = None
    embedding_backend: str | None = None
    hybrid_semantic_backend: str | None = None


def _settings_snapshot(settings: Settings) -> dict[str, Any]:
    return {
        "corpus_filenames": list(settings.corpus_filenames),
        "corpus_subdir": settings.corpus_subdir,
        "chunk_size": settings.chunk_size,
        "chunk_overlap": settings.chunk_overlap,
        "retrieve_top_k": settings.retrieve_top_k,
        "active_profile": settings.active_profile,
        "embedding_backend": settings.embedding_backend,
        "hybrid_semantic_backend": settings.hybrid_semantic_backend,
        "hybrid_rrf_k": settings.hybrid_rrf_k,
        "local_embedding_model": settings.local_embedding_model,
        "llm_backend": settings.llm_backend,
        "llm_model": settings.llm_model,
        "system_prompt_language": settings.system_prompt_language,
        "response_language": settings.response_language,
        "prompt_strategy": settings.prompt_strategy,
        "corpus_sources": settings.corpus_sources,
        "load_processed_jsonl": settings.load_processed_jsonl,
        "corpus_processed_dir": str(settings.corpus_processed_dir),
        "retrieval_use_quotas": settings.retrieval_use_quotas,
        "retrieval_quota_by_doctype": settings.retrieval_quota_by_doctype,
        "retrieval_quota_processed": settings.retrieval_quota_processed,
        "retrieval_quota_pdf": settings.retrieval_quota_pdf,
        "retrieval_quota_rrs": settings.retrieval_quota_rrs,
        "retrieval_quota_call": settings.retrieval_quota_call,
        "retrieval_quota_case": settings.retrieval_quota_case,
        "retrieval_quota_definition": settings.retrieval_quota_definition,
    }


def _run_id(label: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in label)[:40]
    return f"{ts}_{safe}"


def run_evaluation(
    config: EvalRunConfig,
    settings: Settings | None = None,
) -> dict[str, Any]:
    """Corre el golden set, guarda JSON en eval/runs/<run_id>/ y devuelve el reporte."""
    os.environ.setdefault("REGATAS_ACTIVITY_CONSOLE", "0")

    settings = settings or Settings.from_env()
    if config.response_language:
        settings = replace(settings, response_language=config.response_language)
    if config.embedding_backend:
        settings = replace(settings, embedding_backend=config.embedding_backend)
    if config.hybrid_semantic_backend:
        settings = replace(
            settings, hybrid_semantic_backend=config.hybrid_semantic_backend
        )
    eval_data = load_eval_set(config.eval_set_path)
    cases = eval_data["cases"]

    root = Path(__file__).resolve().parents[2]
    runs_dir = config.runs_dir or (root / "eval" / "runs")
    run_id = _run_id(config.label)
    out_dir = runs_dir / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    pipeline = ProtestPipeline.from_settings(settings)
    case_results: list[dict[str, Any]] = []

    for case in cases:
        case_id = case["id"]
        relato = case["relato_protesta"]
        relato_protestado = case.get("relato_protestado")

        trace = pipeline.analyze_trace(
            relato,
            relato_protestado,
            system_prompt_lang=config.system_prompt_lang,
            response_language=config.response_language,
            prompt_strategy=config.prompt_strategy,
            llm_model=config.llm_model,
            skip_llm=config.retrieval_only,
        )

        metrics = score_case(
            expected=case["expected"],
            retrieved=trace["retrieved"],
            answer=trace.get("answer"),
            top_k=settings.retrieve_top_k,
            output_ideal=case.get("output_ideal"),
        )

        if (
            config.compute_faithfulness
            and not config.retrieval_only
            and trace.get("answer")
        ):
            from regatas_assistant.eval.faithfulness import llm_for_judge, score_faithfulness

            judge = llm_for_judge(
                pipeline.llm,
                config.faithfulness_model or config.llm_model,
            )
            try:
                fh = score_faithfulness(
                    judge,
                    trace["answer"],
                    metrics.get("retrieved") or [],
                )
                metrics.setdefault("response", {})["faithfulness"] = fh
            except Exception as exc:
                metrics.setdefault("response", {})["faithfulness"] = {
                    "error": str(exc),
                    "faithfulness_rate": None,
                }

        case_results.append(
            {
                "id": case_id,
                "titulo": case.get("titulo"),
                "relato_protesta": relato,
                "relato_protestado": relato_protestado,
                "expected": case["expected"],
                "output_ideal": case.get("output_ideal"),
                "query": trace["query"],
                "answer": trace.get("answer"),
                "metrics": metrics,
            }
        )

    aggregate = aggregate_metrics(case_results)
    report: dict[str, Any] = {
        "run_id": run_id,
        "label": config.label,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "retrieval_only": config.retrieval_only,
        "eval_set": str(config.eval_set_path or (root / "eval" / "data" / "eval_set.json")),
        "eval_set_source": eval_data.get("source"),
        "settings": _settings_snapshot(settings),
        "aggregate": aggregate,
        "cases": case_results,
    }
    report = enrich_report(report)
    export_sidecars(report, out_dir)

    (out_dir / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (out_dir / "summary.txt").write_text(_format_summary(report), encoding="utf-8")
    return report


def _format_summary(report: dict[str, Any]) -> str:
    agg = report.get("aggregate") or {}
    lines = [
        f"Run: {report.get('run_id')} ({report.get('label')})",
        f"Created: {report.get('created_at')}",
        f"Retrieval only: {report.get('retrieval_only')}",
        f"Cases: {agg.get('n_cases')}",
        "",
        "=== Agregados ===",
        f"Recall@k reglas (media): {_fmt(agg.get('mean_recall_at_k_rules'))}",
        f"Recall@k calls (media):  {_fmt(agg.get('mean_recall_at_k_calls'))}",
        f"F1 citas RRS (media):      {_fmt(agg.get('mean_citation_f1_rrs'))}",
        f"F1 citas Call (media):     {_fmt(agg.get('mean_citation_f1_calls'))}",
        f"Jaccard resp-contexto:     {_fmt(agg.get('mean_token_jaccard_answer_context'))}",
        f"Jaccard resp-referencia:   {_fmt(agg.get('mean_token_jaccard_answer_reference'))}",
        f"Acierto dictamen:          {_fmt(agg.get('verdict_accuracy'))}",
    ]
    if agg.get("mean_faithfulness_rate") is not None:
        lines.extend(
            [
                f"Faithfulness (media):    {_fmt(agg.get('mean_faithfulness_rate'))}",
                f"Faithfulness estricta:   {_fmt(agg.get('mean_faithfulness_rate_strict'))}",
            ]
        )
    lines.extend(
        [
            "",
            "=== Por caso (recall reglas | F1 RRS | verdict) ===",
        ]
    )
    for c in report.get("cases") or []:
        m = c.get("metrics") or {}
        ret = m.get("retrieval") or {}
        resp = m.get("response") or {}
        cit = resp.get("citation_rrs") or {}
        vm = resp.get("verdict_match")
        lines.append(
            f"  {c['id']:>2} {str(c.get('titulo',''))[:42]:<42} "
            f"R@{ret.get('recall_at_k_rules')} "
            f"F1={cit.get('f1')} "
            f"V={'✓' if vm else '✗' if vm is False else '-'}"
        )
    return "\n".join(lines) + "\n"


def _fmt(v: Any) -> str:
    if v is None:
        return "n/a"
    if isinstance(v, float):
        return f"{v:.3f}"
    return str(v)
