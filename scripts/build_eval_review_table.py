#!/usr/bin/env python3
"""Genera tabla Markdown del golden set para revisión manual."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _fmt_list(items: list[str]) -> str:
    return ", ".join(items) if items else "—"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--eval-set",
        type=Path,
        default=ROOT / "eval" / "data" / "eval_set.json",
    )
    p.add_argument(
        "--out",
        type=Path,
        default=ROOT / "eval" / "data" / "golden_set_review.md",
    )
    args = p.parse_args()
    data = json.loads(args.eval_set.read_text(encoding="utf-8"))
    cases = data["cases"]

    lines = [
        "# Golden set — revisión de etiquetas esperadas",
        "",
        f"Fuente: `{data.get('source', '')}`  ",
        f"Generado: `{data.get('built_at', '')}`  ",
        f"Casos: **{len(cases)}**",
        "",
        "| ID | Título | Reglas RRS esperadas | TR CALL | Casos WS | Dictamen | Penaliza |",
        "|----|--------|----------------------|---------|----------|----------|----------|",
    ]
    for c in cases:
        exp = c.get("expected") or {}
        lines.append(
            f"| {c['id']} | {c.get('titulo', '')} | "
            f"{_fmt_list(exp.get('rrs_rules') or [])} | "
            f"{_fmt_list(exp.get('calls') or [])} | "
            f"{_fmt_list(exp.get('cases') or [])} | "
            f"{exp.get('verdict') or '—'} | "
            f"{_fmt_list(exp.get('penalized_boats') or [])} |"
        )

    lines.extend(
        [
            "",
            "## Relatos (Input)",
            "",
        ]
    )
    for c in cases:
        relato = (c.get("relato_protesta") or "").replace("\n", " ")
        lines.append(f"### Caso {c['id']}: {c.get('titulo', '')}")
        lines.append("")
        lines.append(f"> {relato}")
        lines.append("")

    lines.extend(
        [
            "## Output ideal (extracto normativo)",
            "",
            "| ID | Fragmento Norma + Decisión |",
            "|----|------------------------------|",
        ]
    )
    for c in cases:
        out = (c.get("output_ideal") or "").replace("\n", " ")
        if len(out) > 220:
            out = out[:217] + "…"
        lines.append(f"| {c['id']} | {out} |")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Tabla escrita en: {args.out}")


if __name__ == "__main__":
    main()
