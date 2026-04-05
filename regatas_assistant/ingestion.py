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

    def header_line(self) -> str:
        return f"[{self.source_file} — p. {self.page_start} — §{self.chunk_index}]"


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


def load_corpus_chunks(settings: Settings) -> list[TextChunk]:
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
                    )
                )
    return out


def format_chunks_for_prompt(chunks: list[TextChunk]) -> str:
    blocks = []
    for c in chunks:
        blocks.append(f"{c.header_line()}\n{c.text}")
    return "\n\n---\n\n".join(blocks)
