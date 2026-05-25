"""Golden set de evaluación (Casos de Regatas.xlsx → JSON)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from regatas_assistant.eval.refs import (
    extract_calls,
    extract_cases,
    extract_decision,
    extract_penalized_boats,
    extract_rrs_rules,
    normalize_verdict,
)

_DEFAULT_XLSX = Path(__file__).resolve().parents[2] / "docs" / "Casos de Regatas.xlsx"
_DEFAULT_JSON = Path(__file__).resolve().parents[2] / "eval" / "data" / "eval_set.json"


def _load_rows_from_excel(path: Path) -> list[dict[str, Any]]:
    try:
        import pandas as pd
    except ImportError as e:
        raise ImportError(
            "Se requiere pandas y openpyxl para leer el Excel. "
            "Instalá: pip install pandas openpyxl"
        ) from e

    df = pd.read_excel(path, sheet_name=0, header=None)
    rows: list[dict[str, Any]] = []
    for _, row in df.iterrows():
        raw_id = row.iloc[0]
        if raw_id is None or str(raw_id).strip() in ("", "ID", "nan"):
            continue
        try:
            case_id = str(int(raw_id))
        except (TypeError, ValueError):
            continue
        titulo = str(row.iloc[1]).strip() if len(row) > 1 else ""
        relato = str(row.iloc[2]).strip() if len(row) > 2 else ""
        output_ideal = str(row.iloc[3]).strip() if len(row) > 3 else ""
        if not relato:
            continue
        decision = extract_decision(output_ideal)
        rows.append(
            {
                "id": case_id,
                "titulo": titulo,
                "relato_protesta": relato,
                "relato_protestado": None,
                "output_ideal": output_ideal,
                "expected": {
                    "rrs_rules": extract_rrs_rules(output_ideal),
                    "calls": extract_calls(output_ideal),
                    "cases": extract_cases(output_ideal),
                    "decision_text": decision,
                    "verdict": normalize_verdict(decision),
                    "penalized_boats": extract_penalized_boats(decision),
                },
            }
        )
    rows.sort(key=lambda x: int(x["id"]))
    return rows


def build_eval_set_from_excel(
    xlsx_path: Path | None = None,
    out_path: Path | None = None,
) -> dict[str, Any]:
    xlsx = xlsx_path or _DEFAULT_XLSX
    out = out_path or _DEFAULT_JSON
    cases = _load_rows_from_excel(xlsx)
    if not cases:
        raise ValueError(f"No se encontraron casos en {xlsx}")

    payload: dict[str, Any] = {
        "version": 1,
        "source": str(xlsx),
        "built_at": datetime.now(timezone.utc).isoformat(),
        "notes": (
            "relato_protesta = columna Input del Excel; "
            "etiquetas extraídas del Output Ideal Esperado."
        ),
        "cases": cases,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def load_eval_set(path: Path | None = None) -> dict[str, Any]:
    p = path or _DEFAULT_JSON
    if not p.is_file():
        raise FileNotFoundError(
            f"No existe {p}. Ejecutá: python scripts/build_eval_set.py"
        )
    return json.loads(p.read_text(encoding="utf-8"))
