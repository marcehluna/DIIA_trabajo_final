#!/usr/bin/env python3
"""Enriquece report.json existente y exporta CSV/JSON auxiliares para gráficos."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from regatas_assistant.eval.enrich import enrich_report_file  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser(
        description="Añadir metrics.extended y sidecars a una corrida guardada"
    )
    p.add_argument(
        "path",
        type=Path,
        nargs="?",
        default=ROOT / "eval" / "corrida baseline",
        help="Carpeta de corrida o report.json",
    )
    args = p.parse_args()
    out = enrich_report_file(args.path)
    print(f"Reporte enriquecido: {out}")
    print(f"Sidecars en: {out.parent}")


if __name__ == "__main__":
    main()
