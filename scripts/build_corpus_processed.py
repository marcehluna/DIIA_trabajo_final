#!/usr/bin/env python3
"""Genera corpus/processed/*.jsonl desde los CSV del RRS y definiciones."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from regatas_assistant.corpus_processed import build_processed_corpus  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--rrs-csv",
        type=Path,
        default=ROOT / "scripts" / "rrs_reglas_2025_2028.csv",
        help="CSV de reglas RRS",
    )
    p.add_argument(
        "--definitions-csv",
        type=Path,
        default=ROOT / "scripts" / "definitions.csv",
        help="CSV de definiciones",
    )
    p.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT / "corpus" / "processed",
        help="Directorio de salida JSONL",
    )
    p.add_argument(
        "--no-definitions",
        action="store_true",
        help="Omitir definitions.jsonl",
    )
    args = p.parse_args()

    stats = build_processed_corpus(
        ROOT,
        rrs_csv=args.rrs_csv,
        definitions_csv=args.definitions_csv,
        out_dir=args.out_dir,
        include_definitions=not args.no_definitions,
    )
    print(f"Salida: {stats['out_dir']}")
    print(f"  rrs_rules.jsonl: {stats['rrs_rules']} registros")
    print(f"  definitions: {stats.get('definitions', 0)} registros")
    print(f"  manifest: {stats['manifest']}")


if __name__ == "__main__":
    main()
