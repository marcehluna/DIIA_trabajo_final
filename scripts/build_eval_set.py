#!/usr/bin/env python3
"""Genera eval/data/eval_set.json desde docs/Casos de Regatas.xlsx."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from regatas_assistant.eval.golden import build_eval_set_from_excel  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser(description="Construir golden set de evaluación")
    p.add_argument(
        "--xlsx",
        type=Path,
        default=ROOT / "docs" / "Casos de Regatas.xlsx",
        help="Ruta al Excel de casos",
    )
    p.add_argument(
        "--out",
        type=Path,
        default=ROOT / "eval" / "data" / "eval_set.json",
        help="JSON de salida",
    )
    args = p.parse_args()
    data = build_eval_set_from_excel(args.xlsx, args.out)
    n = len(data["cases"])
    print(f"Golden set: {n} casos → {args.out}")
    for c in data["cases"]:
        exp = c["expected"]
        print(
            f"  {c['id']:>2} reglas={exp['rrs_rules']} calls={exp['calls']} "
            f"verdict={exp['verdict']}"
        )


if __name__ == "__main__":
    main()
