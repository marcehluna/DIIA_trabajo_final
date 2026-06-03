#!/usr/bin/env python3
"""Comprueba métricas agregadas de una corrida vs umbrales E11 (regresión)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(ROOT))

from regatas_assistant.profiles import (  # noqa: E402
    E11_REFERENCE_RUN_ID,
    E11_REGRESSION_THRESHOLDS,
)


def _load_aggregate(run_dir: Path) -> dict:
    report = run_dir / "report.json"
    if not report.is_file():
        raise FileNotFoundError(f"No existe {report}")
    data = json.loads(report.read_text(encoding="utf-8"))
    agg = data.get("aggregate") or {}
    return agg, data.get("run_id", run_dir.name)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "run_dir",
        type=Path,
        nargs="?",
        default=ROOT / "eval" / "runs" / E11_REFERENCE_RUN_ID,
        help="Carpeta de corrida (default: referencia E11)",
    )
    p.add_argument(
        "--reference",
        type=Path,
        default=None,
        help=f"Corrida de referencia (default: eval/runs/{E11_REFERENCE_RUN_ID})",
    )
    args = p.parse_args()

    run_dir = args.run_dir.resolve()
    ref_dir = (
        args.reference.resolve()
        if args.reference
        else ROOT / "eval" / "runs" / E11_REFERENCE_RUN_ID
    )

    agg, run_id = _load_aggregate(run_dir)
    ref_agg, ref_id = _load_aggregate(ref_dir) if ref_dir.is_dir() else ({}, "")

    print(f"Corrida: {run_id}")
    if ref_id:
        print(f"Referencia E11: {ref_id}")
    print()
    failed = False
    for key, floor in E11_REGRESSION_THRESHOLDS.items():
        val = agg.get(key)
        ref_val = ref_agg.get(key) if ref_agg else None
        if val is None:
            print(f"  {key}: (sin dato) — SKIP")
            continue
        ok = float(val) >= floor
        ref_note = ""
        if ref_val is not None:
            ref_note = f" (E11={float(ref_val):.3f})"
        status = "OK" if ok else "FAIL"
        print(f"  [{status}] {key}: {float(val):.3f} >= {floor:.3f}{ref_note}")
        if not ok:
            failed = True

    if failed:
        print("\nRegresión: una o más métricas por debajo del umbral E11.")
        return 1
    print("\nRegresión: OK (umbrales E11 cumplidos).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
