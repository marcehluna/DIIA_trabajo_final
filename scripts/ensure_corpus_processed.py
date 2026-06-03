#!/usr/bin/env python3
"""Verifica que exista el corpus JSONL de producción; opcionalmente lo genera."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / "corpus" / "processed"
REQUIRED = (
    "rrs_rules.jsonl",
    "definitions.jsonl",
    "calls.jsonl",
    "cases.jsonl",
)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--build",
        action="store_true",
        help="Ejecutar build_corpus_processed.py si falta algún JSONL",
    )
    args = p.parse_args()

    missing = [name for name in REQUIRED if not (PROCESSED / name).is_file()]
    if not missing:
        print(f"OK: corpus processed completo en {PROCESSED}")
        return 0

    print("Faltan artefactos en corpus/processed/:", ", ".join(missing))
    if not args.build:
        print("Regenerar con: python scripts/build_corpus_processed.py")
        print("O ejecutar este script con --build")
        return 1

    script = ROOT / "scripts" / "build_corpus_processed.py"
    print(f"Ejecutando {script.name} …")
    r = subprocess.run([sys.executable, str(script)], cwd=str(ROOT))
    if r.returncode != 0:
        return r.returncode
    still = [name for name in REQUIRED if not (PROCESSED / name).is_file()]
    if still:
        print("Tras build, siguen faltando:", ", ".join(still))
        return 1
    print("OK: corpus processed generado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
