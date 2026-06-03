"""Extracción de TR CALL desde el PDF del Call Book hacia filas CSV."""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from pypdf import PdfReader

CALL_START_RE = re.compile(r"TR\s+CALL\s+([A-Z]\d+)\b", re.I)
SECTION_RE = re.compile(r"SECTION\s+([A-Z])\s*[–-]\s*([^\n]+)", re.I)
RULE_LINE_RE = re.compile(r"^Rule\s+(.+?)\s*$", re.M)
RULE_NUM_RE = re.compile(
    r"(\d{1,2}(?:\.\d+)*(?:\([a-z]\))*(?:\([0-9]+\))*)|([Dd]\d+(?:\.\d+)*)",
    re.I,
)

DEFAULT_CALL_BOOK_PDF = "corpus/The-Call-Book-for-Team-Racing-2025-2028.pdf"

CSV_FIELDS = (
    "codigo_call",
    "titulo",
    "seccion",
    "reglas",
    "pagina_inicio",
    "pagina_fin",
    "texto",
)


@dataclass(frozen=True)
class CallBookRow:
    codigo_call: str
    titulo: str
    seccion: str
    reglas: str
    pagina_inicio: int
    pagina_fin: int
    texto: str

    def to_csv_dict(self) -> dict[str, str]:
        return {
            "codigo_call": self.codigo_call,
            "titulo": self.titulo,
            "seccion": self.seccion,
            "reglas": self.reglas,
            "pagina_inicio": str(self.pagina_inicio),
            "pagina_fin": str(self.pagina_fin),
            "texto": self.texto,
        }


def _normalize_ws(text: str) -> str:
    return re.sub(r"[ \t]+", " ", text).strip()


def _trim_trailing_section_headers(text: str) -> str:
    """Quita encabezados de sección repetidos al final (artefacto del PDF)."""
    lines = text.splitlines()
    while lines:
        last = lines[-1].strip()
        if not last:
            lines.pop()
            continue
        if SECTION_RE.search(last) or last.upper().startswith("SECTION "):
            lines.pop()
            continue
        break
    return "\n".join(lines)


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
    """Texto concatenado y offsets (char_index, page_num)."""
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


def _section_at(sections: list[tuple[int, str, str]], pos: int) -> str:
    letter = ""
    name = ""
    for start, L, title in sections:
        if start <= pos:
            letter, name = L, title
        else:
            break
    if not name:
        return ""
    return f"SECTION {letter} – {name}"


def _format_call_text(code: str, titulo: str, body: str) -> str:
    header = f"TR CALL {code}"
    if titulo:
        header = f"{header} — {titulo}"
    body = _normalize_block(body)
    if body.upper().startswith(header.upper()):
        return body
    return f"{header}\n\n{body}"


def _titulo_from_rules(rule_lines: list[str], max_rules: int = 2) -> str:
    cleaned = [_normalize_ws(ln) for ln in rule_lines if ln.strip()]
    if not cleaned:
        return ""
    return "; ".join(cleaned[:max_rules])


def extract_calls_from_pdf(pdf_path: Path) -> list[CallBookRow]:
    doc, offsets = _build_document(pdf_path)
    sections = [
        (m.start(), m.group(1).upper(), m.group(2).strip())
        for m in SECTION_RE.finditer(doc)
    ]
    starts = list(CALL_START_RE.finditer(doc))
    if not starts:
        raise ValueError(f"No se encontraron marcadores 'TR CALL' en {pdf_path}")

    rows: list[CallBookRow] = []
    for i, m in enumerate(starts):
        code = m.group(1).upper()
        start_idx = m.start()
        end_idx = starts[i + 1].start() if i + 1 < len(starts) else len(doc)
        block = _trim_trailing_section_headers(doc[m.end() : end_idx].strip())
        rule_lines = RULE_LINE_RE.findall(block[:2500])
        reglas = "|".join(_rule_numbers_from_lines(rule_lines))
        titulo = _titulo_from_rules(rule_lines)
        seccion = _section_at(sections, start_idx)
        texto = _format_call_text(code, titulo, block)
        rows.append(
            CallBookRow(
                codigo_call=code,
                titulo=titulo,
                seccion=seccion,
                reglas=reglas,
                pagina_inicio=_page_at(offsets, start_idx),
                pagina_fin=_page_at(offsets, end_idx),
                texto=texto,
            )
        )
    return rows


def write_calls_csv(rows: list[CallBookRow], out_path: Path) -> int:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS, quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        for row in rows:
            w.writerow(row.to_csv_dict())
    return len(rows)


def read_calls_csv(csv_path: Path) -> Iterator[CallBookRow]:
    with csv_path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            code = (row.get("codigo_call") or "").strip().upper()
            texto = (row.get("texto") or "").strip()
            if not code or not texto:
                continue
            yield CallBookRow(
                codigo_call=code,
                titulo=(row.get("titulo") or "").strip(),
                seccion=(row.get("seccion") or "").strip(),
                reglas=(row.get("reglas") or "").strip(),
                pagina_inicio=int(row.get("pagina_inicio") or 0),
                pagina_fin=int(row.get("pagina_fin") or 0),
                texto=texto,
            )
