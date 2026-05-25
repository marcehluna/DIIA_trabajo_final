"""Enriquece un report.json con datos derivados para gráficos adicionales."""

from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path
from typing import Any

from regatas_assistant.eval.refs import (
    answer_citations,
    chunk_mentions_call,
    chunk_mentions_rule,
    extract_calls,
    extract_rrs_rules,
)

SCHEMA_VERSION = 2


def _first_hit_rank(
    chunks: list[dict[str, Any]],
    *,
    rule: str | None = None,
    call: str | None = None,
) -> int | None:
    for i, ch in enumerate(chunks):
        text = ch.get("text") or ""
        if rule is not None and chunk_mentions_rule(text, rule):
            return i + 1
        if call is not None and chunk_mentions_call(text, call):
            return i + 1
    return None


def _recall_curve(
    expected: list[str],
    chunks: list[dict[str, Any]],
    max_k: int,
    *,
    kind: str,
) -> dict[str, float | None]:
    curve: dict[str, float | None] = {}
    for k in range(1, max_k + 1):
        top = chunks[:k]
        if not expected:
            curve[f"recall_at_{k}"] = None
            continue
        hits = 0
        for item in expected:
            ok = any(
                chunk_mentions_rule(c.get("text") or "", item)
                if kind == "rules"
                else chunk_mentions_call(c.get("text") or "", item)
                for c in top
            )
            if ok:
                hits += 1
        curve[f"recall_at_{k}"] = hits / len(expected)
    return curve


def _mrr(expected: list[str], chunks: list[dict[str, Any]], *, kind: str) -> float | None:
    if not expected:
        return None
    ranks: list[float] = []
    for item in expected:
        r = _first_hit_rank(
            chunks,
            rule=item if kind == "rules" else None,
            call=item if kind == "calls" else None,
        )
        ranks.append(1.0 / r if r else 0.0)
    return sum(ranks) / len(ranks)


def _hit_details(
    expected: list[str],
    chunks: list[dict[str, Any]],
    *,
    kind: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in expected:
        rank = _first_hit_rank(
            chunks,
            rule=item if kind == "rules" else None,
            call=item if kind == "calls" else None,
        )
        chunk_id = None
        if rank is not None:
            ch = chunks[rank - 1]
            chunk_id = ch.get("chunk_id")
        rows.append(
            {
                "expected": item,
                "hit": rank is not None,
                "first_rank": rank,
                "first_chunk_id": chunk_id,
            }
        )
    return rows


def _chunk_rows(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for i, ch in enumerate(chunks):
        text = ch.get("text") or ""
        rows.append(
            {
                "rank": i + 1,
                "chunk_id": ch.get("chunk_id"),
                "source_file": ch.get("source_file"),
                "page_start": ch.get("page_start"),
                "chunk_index": ch.get("chunk_index"),
                "char_len": len(text),
                "refs_in_chunk": {
                    "rrs_rules": extract_rrs_rules(text),
                    "calls": extract_calls(text),
                },
            }
        )
    return rows


def enrich_case(case: dict[str, Any], top_k: int) -> dict[str, Any]:
    """Añade `metrics.extended` sin modificar campos ya usados por plots actuales."""
    m = case.get("metrics") or {}
    chunks = m.get("retrieved") or []
    expected = case.get("expected") or {}
    exp_rules = expected.get("rrs_rules") or []
    exp_calls = expected.get("calls") or []
    answer = case.get("answer") or ""

    by_source: dict[str, int] = {}
    for ch in chunks:
        src = ch.get("source_file") or "unknown"
        by_source[src] = by_source.get(src, 0) + 1

    extended: dict[str, Any] = {
        "recall_curve_rules": _recall_curve(exp_rules, chunks, top_k, kind="rules"),
        "recall_curve_calls": _recall_curve(exp_calls, chunks, top_k, kind="calls"),
        "mrr_rules": _mrr(exp_rules, chunks, kind="rules"),
        "mrr_calls": _mrr(exp_calls, chunks, kind="calls"),
        "rule_hits": _hit_details(exp_rules, chunks, kind="rules"),
        "call_hits": _hit_details(exp_calls, chunks, kind="calls"),
        "retrieved_by_source": by_source,
        "retrieved_chunks_detail": _chunk_rows(chunks),
        "answer_char_len": len(answer) if answer else 0,
        "context_char_len": sum(len(c.get("text") or "") for c in chunks),
        "context_chunk_count": len(chunks),
    }
    if answer:
        extended["answer_refs"] = answer_citations(answer)

    m["extended"] = extended
    case["metrics"] = m
    return case


def enrich_report(report: dict[str, Any]) -> dict[str, Any]:
    top_k = int((report.get("settings") or {}).get("retrieve_top_k") or 8)
    cases = report.get("cases") or []
    for case in cases:
        enrich_case(case, top_k)

    report["schema_version"] = SCHEMA_VERSION
    report["plot_catalog"] = _plot_catalog()
    report["data_files"] = _data_files_manifest()
    return report


def _plot_catalog() -> list[dict[str, str]]:
    return [
        {"id": "recall_curve", "needs": "metrics_long.csv o extended.recall_curve_*"},
        {"id": "mrr_by_case", "needs": "metrics_long.csv (mrr_rules, mrr_calls)"},
        {"id": "hits_per_expected_rule", "needs": "retrieval_hits.json"},
        {"id": "retrieved_source_mix", "needs": "chunks_summary.csv"},
        {"id": "chunk_length_dist", "needs": "chunks_summary.csv"},
        {"id": "citation_precision_recall", "needs": "metrics.response.citation_*"},
        {"id": "expected_vs_found_rules", "needs": "retrieval_hits.json + citations_found"},
        {"id": "compare_runs_delta", "needs": "dos report.json o metrics_long.csv"},
    ]


def _data_files_manifest() -> list[str]:
    return [
        "report.json",
        "metrics_long.csv",
        "retrieval_hits.json",
        "chunks_summary.csv",
        "eval_set_snapshot.json",
        "DATA_MANIFEST.md",
    ]


def export_sidecars(report: dict[str, Any], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    # metrics_long.csv
    long_path = out_dir / "metrics_long.csv"
    fieldnames = [
        "case_id",
        "titulo",
        "metric",
        "value",
        "k",
        "category",
    ]
    rows: list[dict[str, Any]] = []
    for case in report.get("cases") or []:
        cid = case["id"]
        titulo = case.get("titulo") or ""
        m = case.get("metrics") or {}
        ret = m.get("retrieval") or {}
        resp = m.get("response") or {}
        ext = m.get("extended") or {}

        def add(metric: str, value, category: str, k: str = ""):
            if value is not None:
                rows.append(
                    {
                        "case_id": cid,
                        "titulo": titulo,
                        "metric": metric,
                        "value": value,
                        "k": k,
                        "category": category,
                    }
                )

        top_k = int((report.get("settings") or {}).get("retrieve_top_k") or 8)
        add("recall_at_k_rules", ret.get("recall_at_k_rules"), "retrieval", str(top_k))
        add("recall_at_k_calls", ret.get("recall_at_k_calls"), "retrieval", str(top_k))
        add("mrr_rules", ext.get("mrr_rules"), "retrieval")
        add("mrr_calls", ext.get("mrr_calls"), "retrieval")
        for key, val in (ext.get("recall_curve_rules") or {}).items():
            k = key.replace("recall_at_", "")
            add(key, val, "retrieval_curve_rules", k)
        for key, val in (ext.get("recall_curve_calls") or {}).items():
            k = key.replace("recall_at_", "")
            add(key, val, "retrieval_curve_calls", k)
        for cit_key, cat in (
            ("citation_rrs", "response_citation_rrs"),
            ("citation_calls", "response_citation_calls"),
            ("citation_cases", "response_citation_cases"),
        ):
            cit = resp.get(cit_key) or {}
            for sub in ("precision", "recall", "f1"):
                add(f"{cit_key}_{sub}", cit.get(sub), cat)
        add("token_jaccard_answer_context", resp.get("token_jaccard_answer_context"), "response")
        add("token_jaccard_answer_reference", resp.get("token_jaccard_answer_reference"), "response")
        add("verdict_match", 1.0 if resp.get("verdict_match") else 0.0 if resp.get("verdict_match") is False else None, "response")
        add("answer_char_len", ext.get("answer_char_len"), "volume")
        add("context_char_len", ext.get("context_char_len"), "volume")

    with long_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    # retrieval_hits.json
    hits = {
        "cases": [
            {
                "id": c["id"],
                "titulo": c.get("titulo"),
                "expected": c.get("expected"),
                "rule_hits": (c.get("metrics") or {}).get("extended", {}).get("rule_hits"),
                "call_hits": (c.get("metrics") or {}).get("extended", {}).get("call_hits"),
                "citations_in_answer": (c.get("metrics") or {})
                .get("response", {})
                .get("citations_found"),
            }
            for c in report.get("cases") or []
        ]
    }
    (out_dir / "retrieval_hits.json").write_text(
        json.dumps(hits, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    # chunks_summary.csv
    chunk_fields = [
        "case_id",
        "rank",
        "chunk_id",
        "source_file",
        "page_start",
        "chunk_index",
        "char_len",
        "refs_rrs",
        "refs_calls",
    ]
    chunk_rows: list[dict[str, Any]] = []
    for case in report.get("cases") or []:
        cid = case["id"]
        for ch in (case.get("metrics") or {}).get("extended", {}).get(
            "retrieved_chunks_detail"
        ) or []:
            refs = ch.get("refs_in_chunk") or {}
            chunk_rows.append(
                {
                    "case_id": cid,
                    "rank": ch.get("rank"),
                    "chunk_id": ch.get("chunk_id"),
                    "source_file": ch.get("source_file"),
                    "page_start": ch.get("page_start"),
                    "chunk_index": ch.get("chunk_index"),
                    "char_len": ch.get("char_len"),
                    "refs_rrs": "|".join(refs.get("rrs_rules") or []),
                    "refs_calls": "|".join(refs.get("calls") or []),
                }
            )
    with (out_dir / "chunks_summary.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=chunk_fields)
        w.writeheader()
        w.writerows(chunk_rows)

    # eval_set snapshot
    eval_path = report.get("eval_set")
    if eval_path and Path(eval_path).is_file():
        shutil.copy2(eval_path, out_dir / "eval_set_snapshot.json")

    _write_manifest(out_dir, report)


def _write_manifest(out_dir: Path, report: dict[str, Any]) -> None:
    lines = [
        "# Datos disponibles — corrida baseline",
        "",
        f"**run_id:** `{report.get('run_id')}`  ",
        f"**schema_version:** {report.get('schema_version', 1)}  ",
        f"**casos:** {len(report.get('cases') or [])}",
        "",
        "## Archivos en esta carpeta",
        "",
        "| Archivo | Contenido |",
        "|---------|-----------|",
        "| `report.json` | Fuente completa: relatos, respuestas, chunks, métricas y `extended` |",
        "| `metrics_long.csv` | Una fila por caso × métrica (ideal para pandas/seaborn) |",
        "| `retrieval_hits.json` | Por caso: regla/CALL esperada → rank del primer hit |",
        "| `chunks_summary.csv` | Cada chunk recuperado: fuente, página, longitud, refs detectadas |",
        "| `eval_set_snapshot.json` | Copia del golden set usado en la corrida |",
        "| `summary.txt` / `results_comparison.md` | Resúmenes legibles |",
        "| `plots/*.png` | Gráficos ya generados |",
        "",
        "## Gráficos adicionales posibles (sin re-ejecutar LLM)",
        "",
    ]
    for item in report.get("plot_catalog") or []:
        lines.append(f"- **{item['id']}**: {item['needs']}")
    lines.append("")
    lines.append("## Campos en `report.json` → `cases[].metrics.extended`")
    lines.append("")
    lines.append(
        "- `recall_curve_rules` / `recall_curve_calls`: recall@1 … recall@k\n"
        "- `mrr_rules` / `mrr_calls`: mean reciprocal rank\n"
        "- `rule_hits` / `call_hits`: detalle por ítem esperado\n"
        "- `retrieved_by_source`: conteo Call vs Case por consulta\n"
        "- `retrieved_chunks_detail`: metadatos de cada fragmento\n"
        "- `answer_refs`: citas extraídas de la respuesta"
    )
    (out_dir / "DATA_MANIFEST.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def enrich_report_file(report_path: Path, *, copy_eval_set: bool = True) -> Path:
    report_path = report_path / "report.json" if report_path.is_dir() else report_path
    out_dir = report_path.parent
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report = enrich_report(report)
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    export_sidecars(report, out_dir)
    return report_path
