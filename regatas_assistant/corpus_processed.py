"""Construcción y carga de fragmentos del corpus pre-procesado (JSONL)."""

from __future__ import annotations

import csv
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterator

from regatas_assistant.chunk_metadata import (
    infer_referenced_rules,
    parse_optional_int,
    parse_rule_list,
    record_from_json_data,
)
from regatas_assistant.ingestion import TextChunk

JSONL_SCHEMA_VERSION = 2

DEFAULT_RRS_CSV = "scripts/rrs_reglas_2025_2028.csv"
DEFAULT_DEFINITIONS_CSV = "scripts/definitions.csv"
DEFAULT_CALLS_CSV = "scripts/call_book_calls.csv"
DEFAULT_CASES_CSV = "scripts/case_book_cases.csv"
RRS_JSONL = "rrs_rules.jsonl"
DEFINITIONS_JSONL = "definitions.jsonl"
CALLS_JSONL = "calls.jsonl"
CASES_JSONL = "cases.jsonl"


@dataclass(frozen=True)
class ProcessedRecord:
    doc_type: str
    ref_id: str
    title: str
    text: str
    source: str
    section: str = ""
    rrs_tipo: str = ""
    referenced_rules: tuple[str, ...] = ()
    page_start: int | None = None
    page_end: int | None = None
    lang: str = "en"

    def to_json(self) -> str:
        payload = asdict(self)
        payload["referenced_rules"] = list(self.referenced_rules)
        return json.dumps(payload, ensure_ascii=False)

    @classmethod
    def from_json(cls, line: str) -> ProcessedRecord:
        data = json.loads(line)
        return cls(**record_from_json_data(data))


def _normalize_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _format_rrs_text(numero_regla: str, titulo: str, texto: str) -> str:
    header = f"Regla {numero_regla}"
    if titulo:
        header = f"{header} — {titulo}"
    body = _normalize_ws(texto)
    if body.lower().startswith(f"regla {numero_regla.lower()}"):
        return body
    if body.lower().startswith(numero_regla.lower()):
        return f"Regla {body}"
    return f"{header}\n\n{body}"


def _format_case_text(codigo: str, titulo: str, texto: str) -> str:
    body = texto.strip()
    header = f"CASE {codigo}"
    if titulo:
        header = f"{header} — {titulo}"
    if body.upper().startswith("CASE "):
        return body
    return f"{header}\n\n{body}"


def _format_call_text(codigo: str, titulo: str, texto: str) -> str:
    body = _normalize_ws(texto) if "\n" not in texto else texto.strip()
    header = f"TR CALL {codigo.upper()}"
    if titulo:
        header = f"{header} — {titulo}"
    if body.upper().startswith("TR CALL"):
        return body
    return f"{header}\n\n{body}"


def _format_definition_text(termino: str, texto: str) -> str:
    body = _normalize_ws(texto)
    term = _normalize_ws(termino)
    if term and term.lower() in body.lower()[: len(term) + 20]:
        return body
    return f"Definition: {term}\n\n{body}" if term else body


def iter_rrs_records(csv_path: Path) -> Iterator[ProcessedRecord]:
    seen: dict[str, int] = {}
    with csv_path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            numero = (row.get("numero_regla") or "").strip()
            texto = (row.get("texto") or "").strip()
            if not numero or not texto:
                continue
            titulo = (row.get("titulo") or "").strip()
            seccion = (row.get("seccion") or "").strip()
            n = seen.get(numero, 0)
            seen[numero] = n + 1
            ref_id = numero if n == 0 else f"{numero}#{n}"
            rules_csv = parse_rule_list(row.get("reglas") or "")
            rules = infer_referenced_rules("rrs", ref_id, texto, rules_csv)
            yield ProcessedRecord(
                doc_type="rrs",
                ref_id=ref_id,
                title=titulo,
                text=_format_rrs_text(numero, titulo, texto),
                source=csv_path.name,
                section=seccion,
                rrs_tipo=(row.get("tipo") or "").strip(),
                referenced_rules=rules,
            )


def iter_case_records(csv_path: Path) -> Iterator[ProcessedRecord]:
    with csv_path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            codigo = (row.get("codigo_case") or "").strip()
            texto = (row.get("texto") or "").strip()
            if not codigo or not texto:
                continue
            titulo = (row.get("titulo") or "").strip()
            seccion = (row.get("seccion") or "").strip()
            rules_csv = parse_rule_list(row.get("reglas") or "")
            rules = infer_referenced_rules("case", codigo, texto, rules_csv)
            yield ProcessedRecord(
                doc_type="case",
                ref_id=codigo,
                title=titulo,
                text=_format_case_text(codigo, titulo, texto),
                source=csv_path.name,
                section=seccion,
                referenced_rules=rules,
                page_start=parse_optional_int(row.get("pagina_inicio")),
                page_end=parse_optional_int(row.get("pagina_fin")),
            )


def iter_call_records(csv_path: Path) -> Iterator[ProcessedRecord]:
    with csv_path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            codigo = (row.get("codigo_call") or "").strip().upper()
            texto = (row.get("texto") or "").strip()
            if not codigo or not texto:
                continue
            titulo = (row.get("titulo") or "").strip()
            seccion = (row.get("seccion") or "").strip()
            rules_csv = parse_rule_list(row.get("reglas") or "")
            rules = infer_referenced_rules("call", codigo, texto, rules_csv)
            yield ProcessedRecord(
                doc_type="call",
                ref_id=codigo,
                title=titulo,
                text=_format_call_text(codigo, titulo, texto),
                source=csv_path.name,
                section=seccion,
                referenced_rules=rules,
                page_start=parse_optional_int(row.get("pagina_inicio")),
                page_end=parse_optional_int(row.get("pagina_fin")),
            )


def iter_definition_records(csv_path: Path) -> Iterator[ProcessedRecord]:
    with csv_path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            termino = (row.get("termino") or "").strip()
            texto = (row.get("texto") or "").strip()
            if not texto:
                continue
            ref = (row.get("id") or termino or "").strip()
            if not ref:
                continue
            yield ProcessedRecord(
                doc_type="definition",
                ref_id=ref,
                title=termino,
                text=_format_definition_text(termino, texto),
                source=csv_path.name,
            )


def write_jsonl(records: Iterator[ProcessedRecord], out_path: Path) -> int:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with out_path.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(rec.to_json() + "\n")
            n += 1
    return n


def build_processed_corpus(
    base_dir: Path,
    *,
    rrs_csv: Path | None = None,
    definitions_csv: Path | None = None,
    calls_csv: Path | None = None,
    cases_csv: Path | None = None,
    out_dir: Path | None = None,
    include_definitions: bool = True,
    include_calls: bool = True,
    include_cases: bool = True,
) -> dict[str, Any]:
    """Genera JSONL en corpus/processed/ desde los CSV fuente."""
    root = base_dir.resolve()
    processed_dir = out_dir or (root / "corpus" / "processed")
    rrs_path = rrs_csv or (root / DEFAULT_RRS_CSV)
    def_path = definitions_csv or (root / DEFAULT_DEFINITIONS_CSV)
    calls_path = calls_csv or (root / DEFAULT_CALLS_CSV)
    cases_path = cases_csv or (root / DEFAULT_CASES_CSV)

    if not rrs_path.is_file():
        raise FileNotFoundError(f"No se encuentra CSV RRS: {rrs_path}")

    stats: dict[str, Any] = {"out_dir": str(processed_dir)}
    stats["rrs_rules"] = write_jsonl(
        iter_rrs_records(rrs_path), processed_dir / RRS_JSONL
    )
    stats["rrs_source"] = str(rrs_path)

    if include_definitions and def_path.is_file():
        stats["definitions"] = write_jsonl(
            iter_definition_records(def_path), processed_dir / DEFINITIONS_JSONL
        )
        stats["definitions_source"] = str(def_path)
    else:
        stats["definitions"] = 0

    if include_calls and calls_path.is_file():
        stats["calls"] = write_jsonl(
            iter_call_records(calls_path), processed_dir / CALLS_JSONL
        )
        stats["calls_source"] = str(calls_path)
    else:
        stats["calls"] = 0

    if include_cases and cases_path.is_file():
        stats["cases"] = write_jsonl(
            iter_case_records(cases_path), processed_dir / CASES_JSONL
        )
        stats["cases_source"] = str(cases_path)
    else:
        stats["cases"] = 0

    manifest = {
        "version": JSONL_SCHEMA_VERSION,
        "schema": "processed_record_v2",
        "rrs_rules": stats["rrs_rules"],
        "definitions": stats.get("definitions", 0),
        "calls": stats.get("calls", 0),
        "cases": stats.get("cases", 0),
        "sources": {
            "rrs": rrs_path.name,
            "definitions": def_path.name if def_path.is_file() else None,
            "calls": calls_path.name if calls_path.is_file() else None,
            "cases": cases_path.name if cases_path.is_file() else None,
        },
    }
    manifest_path = processed_dir / "MANIFEST.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    stats["manifest"] = str(manifest_path)
    return stats


def record_to_chunk(rec: ProcessedRecord, chunk_index: int = 0) -> TextChunk:
    if rec.doc_type == "rrs":
        source_label = f"RRS-2025-2028 ({rec.source})"
    elif rec.doc_type == "call":
        source_label = f"Call-Book-TR ({rec.source})"
    elif rec.doc_type == "case":
        source_label = f"Case-Book-WS ({rec.source})"
    else:
        source_label = rec.source
    return TextChunk(
        source_file=source_label,
        page_start=rec.page_start or 0,
        chunk_index=chunk_index,
        text=rec.text,
        doc_type=rec.doc_type,
        ref_id=rec.ref_id,
        section=rec.section,
        referenced_rules=rec.referenced_rules,
        rrs_tipo=rec.rrs_tipo,
        corpus_page_start=rec.page_start,
        corpus_page_end=rec.page_end,
        lang=rec.lang,
    )


def load_processed_chunks(processed_dir: Path) -> list[TextChunk]:
    """Carga todos los JSONL presentes en corpus/processed/."""
    if not processed_dir.is_dir():
        return []

    chunks: list[TextChunk] = []
    for name in (RRS_JSONL, DEFINITIONS_JSONL, CALLS_JSONL, CASES_JSONL):
        path = processed_dir / name
        if not path.is_file():
            continue
        idx = 0
        with path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = ProcessedRecord.from_json(line)
                chunks.append(record_to_chunk(rec, chunk_index=idx))
                idx += 1
    return chunks
