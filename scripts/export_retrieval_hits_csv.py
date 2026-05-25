#!/usr/bin/env python3
"""Exporta retrieval_hits.json a CSV legibles en Excel."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def export(src: Path, out_dir: Path) -> tuple[Path, Path]:
    data = json.loads(src.read_text(encoding="utf-8"))
    detail_path = out_dir / "retrieval_hits_detail.csv"
    summary_path = out_dir / "retrieval_hits_resumen_casos.csv"

    fieldnames = [
        "case_id",
        "titulo",
        "tipo",
        "esperado",
        "en_contexto_recuperado",
        "rank_primer_chunk",
        "chunk_id",
        "citado_en_respuesta",
        "todas_reglas_citadas",
        "todos_calls_citados",
        "dictamen_esperado",
        "barcos_penalizados_esperados",
    ]
    rows: list[dict] = []

    for case in data["cases"]:
        cid = case["id"]
        titulo = case.get("titulo", "")
        exp = case.get("expected") or {}
        cites = case.get("citations_in_answer") or {}
        cited_rules = set(cites.get("rrs_rules") or [])
        cited_calls = set(cites.get("calls") or [])
        all_rules_str = "|".join(cites.get("rrs_rules") or []) or "—"
        all_calls_str = "|".join(cites.get("calls") or []) or "—"
        verdict = exp.get("verdict") or ""
        boats = "|".join(exp.get("penalized_boats") or []) or "—"

        for h in case.get("rule_hits") or []:
            item = h.get("expected", "")
            rows.append(
                {
                    "case_id": cid,
                    "titulo": titulo,
                    "tipo": "RRS",
                    "esperado": item,
                    "en_contexto_recuperado": "si" if h.get("hit") else "no",
                    "rank_primer_chunk": h.get("first_rank") or "",
                    "chunk_id": h.get("first_chunk_id") or "",
                    "citado_en_respuesta": "si" if item in cited_rules else "no",
                    "todas_reglas_citadas": all_rules_str,
                    "todos_calls_citados": all_calls_str,
                    "dictamen_esperado": verdict,
                    "barcos_penalizados_esperados": boats,
                }
            )
        for h in case.get("call_hits") or []:
            item = h.get("expected", "")
            rows.append(
                {
                    "case_id": cid,
                    "titulo": titulo,
                    "tipo": "CALL",
                    "esperado": item,
                    "en_contexto_recuperado": "si" if h.get("hit") else "no",
                    "rank_primer_chunk": h.get("first_rank") or "",
                    "chunk_id": h.get("first_chunk_id") or "",
                    "citado_en_respuesta": "si" if item in cited_calls else "no",
                    "todas_reglas_citadas": all_rules_str,
                    "todos_calls_citados": all_calls_str,
                    "dictamen_esperado": verdict,
                    "barcos_penalizados_esperados": boats,
                }
            )
        exp_r = {h["expected"] for h in case.get("rule_hits") or []}
        for r in sorted(cited_rules - exp_r):
            rows.append(
                {
                    "case_id": cid,
                    "titulo": titulo,
                    "tipo": "RRS (citado, no en golden)",
                    "esperado": f"— → citó {r}",
                    "en_contexto_recuperado": "",
                    "rank_primer_chunk": "",
                    "chunk_id": "",
                    "citado_en_respuesta": "si",
                    "todas_reglas_citadas": all_rules_str,
                    "todos_calls_citados": all_calls_str,
                    "dictamen_esperado": verdict,
                    "barcos_penalizados_esperados": boats,
                }
            )
        exp_c = {h["expected"] for h in case.get("call_hits") or []}
        for c in sorted(cited_calls - exp_c):
            rows.append(
                {
                    "case_id": cid,
                    "titulo": titulo,
                    "tipo": "CALL (citado, no en golden)",
                    "esperado": f"— → citó {c}",
                    "en_contexto_recuperado": "",
                    "rank_primer_chunk": "",
                    "chunk_id": "",
                    "citado_en_respuesta": "si",
                    "todas_reglas_citadas": all_rules_str,
                    "todos_calls_citados": all_calls_str,
                    "dictamen_esperado": verdict,
                    "barcos_penalizados_esperados": boats,
                }
            )

    with detail_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    fields2 = [
        "case_id",
        "titulo",
        "reglas_esperadas",
        "reglas_en_contexto",
        "reglas_citadas_ok",
        "calls_esperados",
        "calls_en_contexto",
        "calls_citados_ok",
        "reglas_citadas_respuesta",
        "calls_citados_respuesta",
        "dictamen_esperado",
    ]
    rows2: list[dict] = []
    for case in data["cases"]:
        exp = case["expected"]
        cites = case["citations_in_answer"]
        rh = case.get("rule_hits") or []
        ch = case.get("call_hits") or []
        exp_r = [h["expected"] for h in rh]
        exp_c = [h["expected"] for h in ch]
        ctx_r = sum(1 for h in rh if h.get("hit"))
        ctx_c = sum(1 for h in ch if h.get("hit"))
        cit_r = sum(1 for h in rh if h["expected"] in set(cites.get("rrs_rules") or []))
        cit_c = sum(1 for h in ch if h["expected"] in set(cites.get("calls") or []))
        rows2.append(
            {
                "case_id": case["id"],
                "titulo": case.get("titulo", ""),
                "reglas_esperadas": "|".join(exp_r),
                "reglas_en_contexto": f"{ctx_r}/{len(rh)}" if rh else "0/0",
                "reglas_citadas_ok": f"{cit_r}/{len(rh)}" if rh else "0/0",
                "calls_esperados": "|".join(exp_c),
                "calls_en_contexto": f"{ctx_c}/{len(ch)}" if ch else "0/0",
                "calls_citados_ok": f"{cit_c}/{len(ch)}" if ch else "0/0",
                "reglas_citadas_respuesta": "|".join(cites.get("rrs_rules") or []) or "—",
                "calls_citados_respuesta": "|".join(cites.get("calls") or []) or "—",
                "dictamen_esperado": exp.get("verdict", ""),
            }
        )
    with summary_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields2)
        w.writeheader()
        w.writerows(rows2)

    return detail_path, summary_path


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument(
        "json_path",
        type=Path,
        nargs="?",
        default=ROOT / "eval" / "corrida baseline" / "retrieval_hits.json",
    )
    p.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Carpeta de salida (default: misma que el JSON)",
    )
    args = p.parse_args()
    out_dir = args.out_dir or args.json_path.parent
    d, s = export(args.json_path, out_dir)
    print(f"Detalle: {d}")
    print(f"Resumen: {s}")

    try:
        import importlib.util

        agg_path = ROOT / "scripts" / "aggregate_retrieval_hits.py"
        spec = importlib.util.spec_from_file_location("aggregate_retrieval_hits", agg_path)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader
        spec.loader.exec_module(mod)
        plots = mod.process_run(d.parent, d.parent.name)
        print(f"Agregados/gráficos: {plots}")
    except Exception as e:
        print(f"(Opcional) aggregate_retrieval_hits: {e}")


if __name__ == "__main__":
    main()
