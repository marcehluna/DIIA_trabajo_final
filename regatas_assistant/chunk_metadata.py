"""Utilidades para metadatos de chunks (reglas referenciadas, secciones, páginas)."""

from __future__ import annotations

from typing import Any


def parse_optional_int(raw: str | int | None) -> int | None:
    if raw is None or raw == "":
        return None
    if isinstance(raw, int):
        return raw
    s = str(raw).strip()
    if not s:
        return None
    try:
        return int(float(s))
    except ValueError:
        return None


def parse_rule_list(raw: str | list[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    """Normaliza lista de reglas (CSV `reglas` con separador |)."""
    if raw is None:
        return ()
    if isinstance(raw, (list, tuple)):
        pieces = [str(x).strip() for x in raw if str(x).strip()]
    else:
        pieces = [p.strip() for p in str(raw).split("|") if p.strip()]
    out: list[str] = []
    seen: set[str] = set()
    for p in pieces:
        key = p.lower()
        if key not in seen:
            seen.add(key)
            out.append(p)
    return tuple(out)


def primary_rule_id(ref_id: str) -> str:
    return ref_id.split("#", 1)[0].strip()


def infer_referenced_rules(doc_type: str, ref_id: str, text: str, from_csv: tuple[str, ...]) -> tuple[str, ...]:
    """CSV primero; si vacío en call/case, extrae reglas del texto."""
    if from_csv:
        return from_csv
    if doc_type == "rrs" and ref_id:
        return (primary_rule_id(ref_id),)
    if doc_type not in ("call", "case"):
        return ()
    try:
        from regatas_assistant.eval.refs import extract_rrs_rules

        found = extract_rrs_rules(text)
        return tuple(found) if found else ()
    except Exception:
        return ()


def metadata_suffix(
    *,
    section: str = "",
    referenced_rules: tuple[str, ...] = (),
    rrs_tipo: str = "",
    page_start: int | None = None,
    page_end: int | None = None,
    lang: str = "",
    max_section_len: int = 80,
) -> str:
    """Fragmento para encabezados de prompt: ` — Sección: … — Reglas: …`."""
    parts: list[str] = []
    sec = (section or "").strip()
    if sec:
        if len(sec) > max_section_len:
            sec = sec[: max_section_len - 1] + "…"
        parts.append(f"Sección: {sec}")
    if referenced_rules:
        rules = ", ".join(referenced_rules[:12])
        if len(referenced_rules) > 12:
            rules += ", …"
        parts.append(f"Reglas: {rules}")
    tipo = (rrs_tipo or "").strip()
    if tipo and tipo.lower() not in ("regla", "rule"):
        parts.append(f"Tipo: {tipo}")
    if page_start is not None:
        if page_end is not None and page_end != page_start:
            parts.append(f"pp. {page_start}-{page_end}")
        else:
            parts.append(f"p. {page_start}")
    lng = (lang or "").strip()
    if lng and lng.lower() not in ("en", "es"):
        parts.append(f"idioma: {lng}")
    if not parts:
        return ""
    return " — " + " — ".join(parts)


def record_from_json_data(data: dict[str, Any]) -> dict[str, Any]:
    """Campos normalizados al cargar JSONL (v1 y v2)."""
    refs_raw = data.get("referenced_rules")
    if refs_raw is None:
        refs: tuple[str, ...] = ()
    else:
        refs = parse_rule_list(refs_raw)
    return {
        "doc_type": data["doc_type"],
        "ref_id": data["ref_id"],
        "title": data.get("title") or "",
        "text": data["text"],
        "source": data.get("source") or "",
        "section": (data.get("section") or "").strip(),
        "rrs_tipo": (data.get("rrs_tipo") or data.get("tipo") or "").strip(),
        "referenced_rules": refs,
        "page_start": parse_optional_int(data.get("page_start")),
        "page_end": parse_optional_int(data.get("page_end")),
        "lang": (data.get("lang") or "en").strip() or "en",
    }
