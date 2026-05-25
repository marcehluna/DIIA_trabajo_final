"""Construcción y carga de fragmentos del corpus pre-procesado (JSONL)."""

from __future__ import annotations

import csv
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterator

from regatas_assistant.ingestion import TextChunk

DEFAULT_RRS_CSV = "scripts/rrs_reglas_2025_2028.csv"
DEFAULT_DEFINITIONS_CSV = "scripts/definitions.csv"
RRS_JSONL = "rrs_rules.jsonl"
DEFINITIONS_JSONL = "definitions.jsonl"


@dataclass(frozen=True)
class ProcessedRecord:
    doc_type: str
    ref_id: str
    title: str
    text: str
    source: str
    section: str = ""

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)

    @classmethod
    def from_json(cls, line: str) -> ProcessedRecord:
        data = json.loads(line)
        return cls(
            doc_type=data["doc_type"],
            ref_id=data["ref_id"],
            title=data.get("title") or "",
            text=data["text"],
            source=data.get("source") or "",
            section=data.get("section") or "",
        )


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
            yield ProcessedRecord(
                doc_type="rrs",
                ref_id=ref_id,
                title=titulo,
                text=_format_rrs_text(numero, titulo, texto),
                source=csv_path.name,
                section=seccion,
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
    out_dir: Path | None = None,
    include_definitions: bool = True,
) -> dict[str, Any]:
    """Genera JSONL en corpus/processed/ desde los CSV fuente."""
    root = base_dir.resolve()
    processed_dir = out_dir or (root / "corpus" / "processed")
    rrs_path = rrs_csv or (root / DEFAULT_RRS_CSV)
    def_path = definitions_csv or (root / DEFAULT_DEFINITIONS_CSV)

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

    manifest = {
        "version": 1,
        "rrs_rules": stats["rrs_rules"],
        "definitions": stats.get("definitions", 0),
        "sources": {
            "rrs": rrs_path.name,
            "definitions": def_path.name if def_path.is_file() else None,
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
    source_label = f"RRS-2025-2028 ({rec.source})" if rec.doc_type == "rrs" else rec.source
    return TextChunk(
        source_file=source_label,
        page_start=0,
        chunk_index=chunk_index,
        text=rec.text,
        doc_type=rec.doc_type,
        ref_id=rec.ref_id,
    )


def load_processed_chunks(processed_dir: Path) -> list[TextChunk]:
    """Carga todos los JSONL presentes en corpus/processed/."""
    if not processed_dir.is_dir():
        return []

    chunks: list[TextChunk] = []
    for name in (RRS_JSONL, DEFINITIONS_JSONL):
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
