#!/usr/bin/env python3
"""Compara agregados de dos corridas (report.json)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    p = argparse.ArgumentParser(description="Comparar dos corridas de evaluación")
    p.add_argument("run_a", type=Path, help="report.json o carpeta de corrida")
    p.add_argument("run_b", type=Path, help="report.json o carpeta de corrida")
    args = p.parse_args()

    def resolve(p: Path) -> Path:
        if p.is_dir():
            return p / "report.json"
        return p

    a = _load(resolve(args.run_a))
    b = _load(resolve(args.run_b))
    keys = [
        "mean_recall_at_k_rules",
        "mean_recall_at_k_calls",
        "mean_citation_f1_rrs",
        "mean_citation_f1_calls",
        "mean_token_jaccard_answer_context",
        "mean_token_jaccard_answer_reference",
        "verdict_accuracy",
    ]
    print(f"A: {a.get('run_id')} ({a.get('label')})")
    print(f"B: {b.get('run_id')} ({b.get('label')})")
    print()
    print(f"{'métrica':<40} {'A':>8} {'B':>8} {'Δ':>8}")
    print("-" * 68)
    for k in keys:
        va = (a.get("aggregate") or {}).get(k)
        vb = (b.get("aggregate") or {}).get(k)
        if va is None and vb is None:
            continue
        delta = (vb - va) if va is not None and vb is not None else None
        def f(x):
            return "n/a" if x is None else f"{x:.3f}"
        d = "n/a" if delta is None else f"{delta:+.3f}"
        print(f"{k:<40} {f(va):>8} {f(vb):>8} {d:>8}")


if __name__ == "__main__":
    main()
