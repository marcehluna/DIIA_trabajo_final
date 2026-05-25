#!/usr/bin/env python3
"""Tabla comparativa: etiquetas esperadas vs métricas de una corrida."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _fmt(v) -> str:
    if v is None:
        return "—"
    if isinstance(v, float):
        return f"{v:.2f}"
    if isinstance(v, bool):
        return "✓" if v else "✗"
    return str(v)


def write_comparison_table(report_path: Path, out: Path | None = None) -> Path:
    report_path = report_path / "report.json" if report_path.is_dir() else report_path
    report = json.loads(report_path.read_text(encoding="utf-8"))
    out = out or (report_path.parent / "results_comparison.md")

    lines = [
        f"# Comparación esperado vs corrida `{report.get('label')}`",
        "",
        f"Run ID: `{report.get('run_id')}`  ",
        f"Modelo: `{report.get('settings', {}).get('llm_model')}`  ",
        f"Corpus: `{', '.join(report.get('settings', {}).get('corpus_filenames', []))}`",
        "",
        "## Agregados",
        "",
        "| Métrica | Valor |",
        "|---------|-------|",
    ]
    for k, v in (report.get("aggregate") or {}).items():
        if k != "n_cases":
            lines.append(f"| {k} | {_fmt(v)} |")

    lines.extend(
        [
            "",
            "## Por caso",
            "",
            "| ID | Reglas esp. | Recall reglas | CALL esp. | Recall CALL | "
            "F1 RRS | F1 CALL | Jaccard ctx | Dictamen |",
            "|----|-------------|---------------|-----------|-------------|"
            "--------|---------|-------------|----------|",
        ]
    )

    for c in report.get("cases") or []:
        exp = c.get("expected") or {}
        m = c.get("metrics") or {}
        ret = m.get("retrieval") or {}
        resp = m.get("response") or {}
        rules_e = ", ".join(exp.get("rrs_rules") or []) or "—"
        calls_e = ", ".join(exp.get("calls") or []) or "—"
        lines.append(
            f"| {c['id']} | {rules_e} | {_fmt(ret.get('recall_at_k_rules'))} | "
            f"{calls_e} | {_fmt(ret.get('recall_at_k_calls'))} | "
            f"{_fmt((resp.get('citation_rrs') or {}).get('f1'))} | "
            f"{_fmt((resp.get('citation_calls') or {}).get('f1'))} | "
            f"{_fmt(resp.get('token_jaccard_answer_context'))} | "
            f"{_fmt(resp.get('verdict_match'))} |"
        )

    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    export_comparison_csv(report, out.parent)
    return out


def export_comparison_csv(report: dict, out_dir: Path) -> tuple[Path, Path]:
    """CSV equivalentes a results_comparison.md (agregados + por caso)."""
    meta_path = out_dir / "results_comparison_meta.csv"
    cases_path = out_dir / "results_comparison_por_caso.csv"

    settings = report.get("settings") or {}
    with meta_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["campo", "valor"])
        w.writerow(["run_id", report.get("run_id", "")])
        w.writerow(["label", report.get("label", "")])
        w.writerow(["created_at", report.get("created_at", "")])
        w.writerow(["modelo", settings.get("llm_model", "")])
        w.writerow(["corpus", ", ".join(settings.get("corpus_filenames") or [])])
        w.writerow(["chunk_size", settings.get("chunk_size", "")])
        w.writerow(["chunk_overlap", settings.get("chunk_overlap", "")])
        w.writerow(["retrieve_top_k", settings.get("retrieve_top_k", "")])
        w.writerow(["embedding_backend", settings.get("embedding_backend", "")])
        w.writerow(["prompt_lang", settings.get("system_prompt_language", "")])
        w.writerow(["prompt_strategy", settings.get("prompt_strategy", "")])
        w.writerow([])
        w.writerow(["metrica", "valor"])
        for k, v in (report.get("aggregate") or {}).items():
            w.writerow([k, v if v is not None else ""])

    fieldnames = [
        "case_id",
        "titulo",
        "reglas_esperadas",
        "calls_esperados",
        "casos_ws_esperados",
        "dictamen_esperado",
        "barcos_penalizados_esperados",
        "recall_reglas_at_k",
        "recall_calls_at_k",
        "f1_citas_rrs",
        "precision_citas_rrs",
        "recall_citas_rrs",
        "f1_citas_call",
        "precision_citas_call",
        "recall_citas_call",
        "jaccard_respuesta_contexto",
        "jaccard_respuesta_referencia",
        "reglas_citadas_en_respuesta",
        "calls_citados_en_respuesta",
        "dictamen_predicho",
        "dictamen_coincide",
        "mrr_reglas",
        "mrr_calls",
    ]
    rows: list[dict] = []
    for c in report.get("cases") or []:
        exp = c.get("expected") or {}
        m = c.get("metrics") or {}
        ret = m.get("retrieval") or {}
        resp = m.get("response") or {}
        ext = m.get("extended") or {}
        cit_r = resp.get("citation_rrs") or {}
        cit_c = resp.get("citation_calls") or {}
        cites = resp.get("citations_found") or {}
        vm = resp.get("verdict_match")
        rows.append(
            {
                "case_id": c["id"],
                "titulo": c.get("titulo", ""),
                "reglas_esperadas": "|".join(exp.get("rrs_rules") or []),
                "calls_esperados": "|".join(exp.get("calls") or []),
                "casos_ws_esperados": "|".join(exp.get("cases") or []),
                "dictamen_esperado": exp.get("verdict") or "",
                "barcos_penalizados_esperados": "|".join(exp.get("penalized_boats") or []),
                "recall_reglas_at_k": ret.get("recall_at_k_rules"),
                "recall_calls_at_k": ret.get("recall_at_k_calls"),
                "f1_citas_rrs": cit_r.get("f1"),
                "precision_citas_rrs": cit_r.get("precision"),
                "recall_citas_rrs": cit_r.get("recall"),
                "f1_citas_call": cit_c.get("f1"),
                "precision_citas_call": cit_c.get("precision"),
                "recall_citas_call": cit_c.get("recall"),
                "jaccard_respuesta_contexto": resp.get("token_jaccard_answer_context"),
                "jaccard_respuesta_referencia": resp.get("token_jaccard_answer_reference"),
                "reglas_citadas_en_respuesta": "|".join(cites.get("rrs_rules") or []),
                "calls_citados_en_respuesta": "|".join(cites.get("calls") or []),
                "dictamen_predicho": resp.get("verdict_predicted") or "",
                "dictamen_coincide": "si" if vm else "no" if vm is False else "",
                "mrr_reglas": ext.get("mrr_rules"),
                "mrr_calls": ext.get("mrr_calls"),
            }
        )

    with cases_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    return meta_path, cases_path


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("report", type=Path, help="Carpeta de corrida o report.json")
    p.add_argument("--out", type=Path, default=None)
    args = p.parse_args()
    report_path = args.report / "report.json" if args.report.is_dir() else args.report
    report = json.loads(report_path.read_text(encoding="utf-8"))
    out_md = args.out or (report_path.parent / "results_comparison.md")
    write_comparison_table(args.report, out_md)
    meta, cases = export_comparison_csv(report, out_md.parent)
    print(f"Markdown: {out_md}")
    print(f"CSV agregados: {meta}")
    print(f"CSV por caso: {cases}")


if __name__ == "__main__":
    main()
