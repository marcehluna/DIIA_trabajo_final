#!/usr/bin/env python3
"""Comprueba métricas agregadas de una corrida vs umbrales de producción (E11 + E13)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(ROOT))

from regatas_assistant.profiles import (  # noqa: E402
    PRODUCTION_REGRESSION_THRESHOLDS,
    RESPONSE_REFERENCE_RUN_ID,
    RESPONSE_REGRESSION_THRESHOLDS,
    RETRIEVAL_REFERENCE_RUN_ID,
    RETRIEVAL_REGRESSION_THRESHOLDS,
)

_METRIC_REF: dict[str, tuple[str, str]] = {}
for key in RETRIEVAL_REGRESSION_THRESHOLDS:
    _METRIC_REF[key] = ("E11", RETRIEVAL_REFERENCE_RUN_ID)
for key in RESPONSE_REGRESSION_THRESHOLDS:
    _METRIC_REF[key] = ("E13", RESPONSE_REFERENCE_RUN_ID)


def _load_aggregate(run_dir: Path) -> dict:
    report = run_dir / "report.json"
    if not report.is_file():
        raise FileNotFoundError(f"No existe {report}")
    data = json.loads(report.read_text(encoding="utf-8"))
    agg = data.get("aggregate") or {}
    return agg, data.get("run_id", run_dir.name)


def main() -> int:
    p = argparse.ArgumentParser(
        description=(
            "Regresión: retrieval (pisos E11) + respuesta (pisos E13). "
            "F1 RRS asume parser actual en refs.py (re-score si la corrida es antigua)."
        )
    )
    p.add_argument(
        "run_dir",
        type=Path,
        nargs="?",
        default=ROOT / "eval" / "runs" / RESPONSE_REFERENCE_RUN_ID,
        help="Carpeta con report.json (default: referencia E13)",
    )
    p.add_argument(
        "--mode",
        choices=("all", "retrieval", "response"),
        default="all",
        help="all=retrieval+respuesta (E13+); retrieval=solo E11; response=solo métricas E13",
    )
    args = p.parse_args()

    if args.mode == "retrieval":
        thresholds = RETRIEVAL_REGRESSION_THRESHOLDS
    elif args.mode == "response":
        thresholds = RESPONSE_REGRESSION_THRESHOLDS
    else:
        thresholds = PRODUCTION_REGRESSION_THRESHOLDS

    run_dir = args.run_dir.resolve()
    ref_dirs = {
        "E11": ROOT / "eval" / "runs" / RETRIEVAL_REFERENCE_RUN_ID,
        "E13": ROOT / "eval" / "runs" / RESPONSE_REFERENCE_RUN_ID,
    }
    ref_aggs: dict[str, dict] = {}
    for label, path in ref_dirs.items():
        if path.is_dir():
            ref_aggs[label], _ = _load_aggregate(path)

    agg, run_id = _load_aggregate(run_dir)

    print(f"Corrida: {run_id}")
    print(f"Modo: {args.mode}")
    print(
        f"Referencias: E11 retrieval ({RETRIEVAL_REFERENCE_RUN_ID}), "
        f"E13 respuesta ({RESPONSE_REFERENCE_RUN_ID})"
    )
    print()
    failed = False
    for key, floor in thresholds.items():
        val = agg.get(key)
        if val is None:
            print(f"  {key}: (sin dato) — SKIP")
            continue
        ref_label, _ = _METRIC_REF.get(key, ("", ""))
        ref_val = ref_aggs.get(ref_label, {}).get(key) if ref_label else None
        ok = float(val) >= floor
        ref_note = ""
        if ref_val is not None and ref_label:
            ref_note = f" ({ref_label}={float(ref_val):.3f})"
        group = "retrieval" if key in RETRIEVAL_REGRESSION_THRESHOLDS else "respuesta"
        status = "OK" if ok else "FAIL"
        print(
            f"  [{status}] [{group}] {key}: {float(val):.3f} >= {floor:.3f}{ref_note}"
        )
        if not ok:
            failed = True

    if failed:
        print("\nRegresión: una o más métricas por debajo del umbral.")
        return 1
    labels = {
        "all": "E11 retrieval + E13 respuesta",
        "retrieval": "E11 retrieval",
        "response": "E13 respuesta",
    }
    print(f"\nRegresión: OK ({labels[args.mode]}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
