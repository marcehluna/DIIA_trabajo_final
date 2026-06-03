"""Extracción de texto desde PDFs del corpus y división en chunks."""

from __future__ import annotations

import re
from dataclasses import dataclass

from pypdf import PdfReader

from regatas_assistant.config import Settings


@dataclass(frozen=True)
class TextChunk:
    source_file: str
    page_start: int
    chunk_index: int
    text: str
    doc_type: str | None = None
    ref_id: str | None = None
    # Metadatos estructurados (JSONL v2 / CSV)
    section: str = ""
    referenced_rules: tuple[str, ...] = ()
    rrs_tipo: str = ""
    corpus_page_start: int | None = None
    corpus_page_end: int | None = None
    lang: str = "en"

    def chunk_id(self) -> str:
        if self.doc_type in ("rrs", "definition", "call", "case") and self.ref_id:
            return f"{self.doc_type}|{self.ref_id}"
        return f"{self.source_file}|p{self.page_start}|#{self.chunk_index}"

    def rule_label(self) -> str | None:
        """Número de regla sin sufijo #n (para matching con el golden set)."""
        if self.doc_type != "rrs" or not self.ref_id:
            return None
        return self.ref_id.split("#", 1)[0]

    def header_line(self) -> str:
        from regatas_assistant.chunk_metadata import metadata_suffix

        meta = metadata_suffix(
            section=self.section,
            referenced_rules=self.referenced_rules,
            rrs_tipo=self.rrs_tipo,
            page_start=self.corpus_page_start,
            page_end=self.corpus_page_end,
            lang=self.lang,
        )
        if self.doc_type == "rrs" and self.ref_id:
            label = self.rule_label() or self.ref_id
            return f"[RRS — Regla {label}{meta} — {self.source_file}]"
        if self.doc_type == "definition" and self.ref_id:
            title = self.ref_id
            return f"[Definición — {title}{meta} — {self.source_file}]"
        if self.doc_type == "call" and self.ref_id:
            return f"[TR CALL {self.ref_id}{meta} — {self.source_file}]"
        if self.doc_type == "case" and self.ref_id:
            return f"[CASE {self.ref_id}{meta} — {self.source_file}]"
        return f"[{self.source_file} — p. {self.page_start} — §{self.chunk_index}{meta}]"


def _read_pdf_pages(path) -> list[tuple[int, str]]:
    reader = PdfReader(str(path))
    pages: list[tuple[int, str]] = []
    for i, page in enumerate(reader.pages):
        raw = page.extract_text() or ""
        text = re.sub(r"\s+", " ", raw).strip()
        if text:
            pages.append((i + 1, text))
    return pages


def _split_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    if chunk_size <= 0:
        return [text] if text else []
    if overlap >= chunk_size:
        overlap = max(0, chunk_size // 4)
    chunks: list[str] = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= n:
            break
        start = end - overlap
        if start < 0:
            start = 0
    return chunks


def _load_pdf_chunks(settings: Settings) -> list[TextChunk]:
    out: list[TextChunk] = []
    for path in settings.corpus_paths:
        if not path.is_file():
            raise FileNotFoundError(f"No se encuentra el corpus: {path}")
        source_name = path.name
        for page_num, page_text in _read_pdf_pages(path):
            parts = _split_text(page_text, settings.chunk_size, settings.chunk_overlap)
            for idx, part in enumerate(parts):
                out.append(
                    TextChunk(
                        source_file=source_name,
                        page_start=page_num,
                        chunk_index=idx,
                        text=part,
                        doc_type="pdf",
                    )
                )
    return out


def load_corpus_chunks(settings: Settings) -> list[TextChunk]:
    """Construye el índice según `settings.corpus_sources` (processed | pdf | full)."""
    from regatas_assistant.config import (
        CORPUS_SOURCES_FULL,
        CORPUS_SOURCES_PDF,
        CORPUS_SOURCES_PROCESSED,
    )
    from regatas_assistant.corpus_processed import load_processed_chunks

    mode = settings.corpus_sources
    out: list[TextChunk] = []

    if mode in (CORPUS_SOURCES_PROCESSED, CORPUS_SOURCES_FULL) and settings.load_processed_jsonl:
        processed = load_processed_chunks(settings.corpus_processed_dir)
        if not processed and mode == CORPUS_SOURCES_PROCESSED:
            raise FileNotFoundError(
                "Modo corpus «processed»: no hay JSONL en "
                f"{settings.corpus_processed_dir}. Ejecutá: "
                "python scripts/build_corpus_processed.py"
            )
        out.extend(processed)

    if mode in (CORPUS_SOURCES_PDF, CORPUS_SOURCES_FULL) and settings.corpus_filenames:
        out.extend(_load_pdf_chunks(settings))

    if not out:
        raise ValueError(
            f"Índice RAG vacío (corpus_sources={mode!r}). "
            "Revisá REGATAS_CORPUS_SOURCES, REGATAS_LOAD_PROCESSED y REGATAS_CORPUS_FILES."
        )
    return out


def corpus_chunk_summary(chunks: list[TextChunk]) -> dict[str, int]:
    """Conteo por doc_type para diagnóstico."""
    counts: dict[str, int] = {}
    for c in chunks:
        key = c.doc_type or "unknown"
        counts[key] = counts.get(key, 0) + 1
    counts["total"] = len(chunks)
    return counts


def format_chunks_for_prompt(chunks: list[TextChunk]) -> str:
    blocks = []
    for c in chunks:
        blocks.append(f"{c.header_line()}\n{c.text}")
    return "\n\n---\n\n".join(blocks)
