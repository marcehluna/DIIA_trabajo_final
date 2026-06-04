#!/usr/bin/env python3
"""Recalcula métricas de citas (y agregados) en report.json sin volver a ejecutar el LLM."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from regatas_assistant.eval.enrich import enrich_report, export_sidecars  # noqa: E402
from regatas_assistant.eval.metrics import aggregate_metrics, score_case  # noqa: E402
from regatas_assistant.ingestion import TextChunk  # noqa: E402


def _chunk_from_dict(d: dict) -> TextChunk:
    return TextChunk(
        source_file=d.get("source_file") or "",
        page_start=int(d.get("page_start") or 0),
        chunk_index=int(d.get("chunk_index") or 0),
        text=d.get("text") or "",
        doc_type=d.get("doc_type"),
        ref_id=d.get("ref_id"),
        section=d.get("section") or "",
        referenced_rules=tuple(d.get("referenced_rules") or ()),
        rrs_tipo=d.get("rrs_tipo") or "",
        corpus_page_start=d.get("corpus_page_start"),
        corpus_page_end=d.get("corpus_page_end"),
        lang=d.get("lang") or "en",
    )


def rescore_report(run_dir: Path, *, top_k: int = 8) -> dict:
    run_dir = run_dir.resolve()
    report_path = run_dir / "report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))

    for case in report.get("cases") or []:
        retrieved_raw = (case.get("metrics") or {}).get("retrieved") or []
        chunks = [_chunk_from_dict(d) for d in retrieved_raw]
        new_metrics = score_case(
            expected=case["expected"],
            retrieved=chunks,
            answer=case.get("answer"),
            top_k=top_k,
            output_ideal=case.get("output_ideal"),
        )
        # Preservar faithfulness y otros campos no recalculados por score_case
        old_resp = (case.get("metrics") or {}).get("response") or {}
        new_resp = new_metrics.get("response") or {}
        if "faithfulness" in old_resp:
            new_resp["faithfulness"] = old_resp["faithfulness"]
        case["metrics"] = {
            "retrieval": new_metrics.get("retrieval") or {},
            "response": new_resp,
            "retrieved": retrieved_raw,
        }

    report["aggregate"] = aggregate_metrics(report.get("cases") or [])
    report = enrich_report(report)
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    export_sidecars(report, run_dir)
    return report


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("run_dir", type=Path, nargs="+", help="Carpeta(s) con report.json")
    p.add_argument("--top-k", type=int, default=8)
    args = p.parse_args()

    for run_dir in args.run_dir:
        report = rescore_report(run_dir, top_k=args.top_k)
        agg = report.get("aggregate") or {}
        print(f"\n{run_dir.name}")
        print(f"  F1 RRS:  {agg.get('mean_citation_f1_rrs')}")
        print(f"  F1 CALL: {agg.get('mean_citation_f1_calls')}")
        print(f"  Dictamen: {agg.get('verdict_accuracy')}")
        print(f"  Actualizado: {run_dir / 'report.json'}")


if __name__ == "__main__":
    main()
