#!/usr/bin/env python3
"""Genera scripts/case_book_cases.csv desde el PDF del WS Case Book (revisión manual)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from regatas_assistant.case_book_extract import (  # noqa: E402
    DEFAULT_CASE_BOOK_PDF,
    extract_cases_from_pdf,
    write_cases_csv,
)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--pdf",
        type=Path,
        default=ROOT / DEFAULT_CASE_BOOK_PDF,
        help="PDF fuente del Case Book",
    )
    p.add_argument(
        "--out-csv",
        type=Path,
        default=ROOT / "scripts" / "case_book_cases.csv",
        help="CSV de salida para revisar/editar",
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="Sobrescribir CSV existente",
    )
    args = p.parse_args()

    if not args.pdf.is_file():
        raise SystemExit(f"No se encuentra el PDF: {args.pdf}")

    if args.out_csv.is_file() and not args.force:
        raise SystemExit(
            f"Ya existe {args.out_csv}. Usá --force para regenerar desde el PDF."
        )

    rows = extract_cases_from_pdf(args.pdf)
    n = write_cases_csv(rows, args.out_csv)
    print(f"CSV: {args.out_csv} ({n} cases)")
    print(
        "Columnas: codigo_case, titulo, seccion, reglas, "
        "pagina_inicio, pagina_fin, texto"
    )
    print("Siguiente paso: revisar el CSV y luego:")
    print("  python scripts/build_corpus_processed.py")


if __name__ == "__main__":
    main()
