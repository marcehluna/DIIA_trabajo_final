#!/usr/bin/env python3
"""Regenera eval/DIARIO_PRUEBAS.md desde todas las corridas en eval/runs/."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from regatas_assistant.eval.diario import (  # noqa: E402
    REGISTRY_JSON,
    regenerate_all,
    update_diario_after_run,
)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "run_dir",
        type=Path,
        nargs="?",
        help="Carpeta de una corrida (con report.json). Si se omite, usa --all.",
    )
    p.add_argument(
        "--all",
        action="store_true",
        help="Regenerar desde todas las corridas conocidas",
    )
    p.add_argument("--nota", default="", help="Nota manual para esta corrida")
    args = p.parse_args()

    if args.all or args.run_dir is None:
        out = regenerate_all()
        print(f"Diario regenerado: {out}")
        if REGISTRY_JSON.is_file():
            print(f"Registro: {REGISTRY_JSON}")
        return

    out = update_diario_after_run(args.run_dir.resolve(), nota=args.nota)
    print(f"Diario actualizado: {out}")
    print(f"Comparación en carpeta: {args.run_dir / 'comparacion_vs_baseline.md'}")


if __name__ == "__main__":
    main()
