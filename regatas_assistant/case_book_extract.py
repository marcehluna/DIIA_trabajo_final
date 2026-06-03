"""Extracción de CASE N desde el PDF del WS Case Book hacia filas CSV."""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from pypdf import PdfReader

CASE_SPLIT_RE = re.compile(r"(?m)(?:^|\n)\s*CASE\s+(\d{1,4})\s*\n")
RULE_LINE_RE = re.compile(r"^Rule\s+(.+?)\s*$", re.M)
RULE_NUM_RE = re.compile(
    r"(\d{1,2}(?:\.\d+)*(?:\([a-z]\))*(?:\([0-9]+\))*)|([Dd]\d+(?:\.\d+)*)",
    re.I,
)

DEFAULT_CASE_BOOK_PDF = "corpus/WS-Case-Book-2025-2028-v2025-07.pdf"

CSV_FIELDS = (
    "codigo_case",
    "titulo",
    "seccion",
    "reglas",
    "pagina_inicio",
    "pagina_fin",
    "texto",
)


@dataclass(frozen=True)
class CaseBookRow:
    codigo_case: str
    titulo: str
    seccion: str
    reglas: str
    pagina_inicio: int
    pagina_fin: int
    texto: str

    def to_csv_dict(self) -> dict[str, str]:
        return {
            "codigo_case": self.codigo_case,
            "titulo": self.titulo,
            "seccion": self.seccion,
            "reglas": self.reglas,
            "pagina_inicio": str(self.pagina_inicio),
            "pagina_fin": str(self.pagina_fin),
            "texto": self.texto,
        }


def _normalize_ws(text: str) -> str:
    return re.sub(r"[ \t]+", " ", text).strip()


def _normalize_block(text: str) -> str:
    lines = [ln.strip() for ln in text.splitlines()]
    out: list[str] = []
    buf: list[str] = []
    for ln in lines:
        if not ln:
            if buf:
                out.append(_normalize_ws(" ".join(buf)))
                buf = []
            continue
        buf.append(ln)
    if buf:
        out.append(_normalize_ws(" ".join(buf)))
    return "\n\n".join(out)


def _rule_numbers_from_lines(rule_lines: list[str]) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    for line in rule_lines:
        for m in RULE_NUM_RE.finditer(line):
            token = (m.group(1) or m.group(2) or "").strip()
            if token and token.lower() not in seen:
                seen.add(token.lower())
                found.append(token)
    return found


def _build_document(pdf_path: Path) -> tuple[str, list[tuple[int, int]]]:
    reader = PdfReader(str(pdf_path))
    parts: list[str] = []
    offsets: list[tuple[int, int]] = []
    pos = 0
    for i, page in enumerate(reader.pages):
        raw = page.extract_text() or ""
        offsets.append((pos, i + 1))
        parts.append(raw)
        pos += len(raw) + 1
    return "\n".join(parts), offsets


def _page_at(offsets: list[tuple[int, int]], idx: int) -> int:
    page = 1
    for start, pnum in offsets:
        if idx >= start:
            page = pnum
    return page


def _titulo_from_body(body: str) -> str:
    """Primera frase o párrafo tras encabezados Rule."""
    lines = [ln.strip() for ln in body.splitlines() if ln.strip()]
    skip_prefixes = ("rule ", "facts", "question", "answer", "case ")
    for ln in lines:
        low = ln.lower()
        if any(low.startswith(p) for p in skip_prefixes):
            continue
        if len(ln) < 20:
            continue
        return _normalize_ws(ln)[:300]
    for ln in lines:
        if not ln.lower().startswith("rule "):
            return _normalize_ws(ln)[:300]
    return ""


def _section_from_context(doc: str, start_idx: int) -> str:
    """Última línea 'Rule …' inmediatamente antes del CASE."""
    prefix = doc[max(0, start_idx - 1200) : start_idx]
    rules = RULE_LINE_RE.findall(prefix)
    if not rules:
        return ""
    return _normalize_ws(rules[-1])


def _format_case_text(code: str, titulo: str, body: str) -> str:
    header = f"CASE {code}"
    if titulo:
        header = f"{header} — {titulo}"
    body_norm = _normalize_block(body)
    if body_norm.upper().startswith("CASE "):
        return body_norm
    return f"{header}\n\n{body_norm}"


def extract_cases_from_pdf(pdf_path: Path) -> list[CaseBookRow]:
    doc, offsets = _build_document(pdf_path)
    matches = list(CASE_SPLIT_RE.finditer(doc))
    if not matches:
        raise ValueError(f"No se encontraron bloques 'CASE N' en {pdf_path}")

    by_code: dict[str, tuple[int, int, str, str]] = {}
    for i, m in enumerate(matches):
        code = m.group(1)
        start_idx = m.start()
        end_idx = matches[i + 1].start() if i + 1 < len(matches) else len(doc)
        block = doc[m.end() : end_idx].strip()
        if len(block) < 80:
            continue
        rule_lines = RULE_LINE_RE.findall(block[:3000])
        reglas = "|".join(_rule_numbers_from_lines(rule_lines))
        titulo = _titulo_from_body(block)
        seccion = _section_from_context(doc, start_idx)
        texto = _format_case_text(code, titulo, block)
        p0 = _page_at(offsets, start_idx)
        p1 = _page_at(offsets, end_idx)
        prev = by_code.get(code)
        if prev is None or len(texto) > len(prev[3]):
            by_code[code] = (p0, p1, titulo, texto, seccion, reglas)

    rows: list[CaseBookRow] = []
    for code in sorted(by_code.keys(), key=lambda c: int(c)):
        p0, p1, titulo, texto, seccion, reglas = by_code[code]
        rows.append(
            CaseBookRow(
                codigo_case=code,
                titulo=titulo,
                seccion=seccion,
                reglas=reglas,
                pagina_inicio=p0,
                pagina_fin=p1,
                texto=texto,
            )
        )
    return rows


def write_cases_csv(rows: list[CaseBookRow], out_path: Path) -> int:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS, quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        for row in rows:
            w.writerow(row.to_csv_dict())
    return len(rows)


def read_cases_csv(csv_path: Path) -> Iterator[CaseBookRow]:
    with csv_path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            code = (row.get("codigo_case") or "").strip()
            texto = (row.get("texto") or "").strip()
            if not code or not texto:
                continue
            yield CaseBookRow(
                codigo_case=code,
                titulo=(row.get("titulo") or "").strip(),
                seccion=(row.get("seccion") or "").strip(),
                reglas=(row.get("reglas") or "").strip(),
                pagina_inicio=int(row.get("pagina_inicio") or 0),
                pagina_fin=int(row.get("pagina_fin") or 0),
                texto=texto,
            )
