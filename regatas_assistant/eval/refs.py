"""Extracción de referencias normativas (RRS, Call, Case) desde texto."""

from __future__ import annotations

import re

# Reglas RRS: "Regla 16.1", "Reglas 11 o 13", "Regla 18.2(a)(2)", "Regla D1.1(e)"
_RRS_BLOCK_RE = re.compile(
    r"(?i)reglas?\s+(.+?)"
    r"(?=\s+seg[uú]n\s+(?:TR\s+)?CALL|\nRationale|\nDecisi[oó]n|$)"
)
_RRS_TOKEN_RE = re.compile(
    r"(\d{1,2}(?:\.\d+)*(?:\([a-z]\))*(?:\([0-9]+\))*)|([Dd]\d+(?:\.\d+)*(?:\([a-z]\))*(?:\([0-9]+\))*)",
    re.I,
)
_CALL_RE = re.compile(r"(?i)(?:TR\s+)?CALL\s+([A-Z]?\d+[A-Z]?)")
_CASE_RE = re.compile(r"(?i)\bcase\s+(\d{1,4})\b")
_RULE_EN_RE = re.compile(
    r"(?i)\b(?:rule|r\.)\s*(\d{1,2}(?:\.\d+)*|[Dd]\d+(?:\.\d+)*)"
)
_DECISION_RE = re.compile(r"(?i)decisi[oó]n:\s*(.+?)(?:\s*$|\n)")
# Prompt v3 / E11: - **Regla 16.1** —, - **Regla RRS 11**:
_REGLA_MARKDOWN_RE = re.compile(r"(?i)\*\*Regla(?:\s+RRS)?\s+([^*]+?)\*\*")
# Líneas tipo "- Regla 16.1 —" (con o sin negritas)
_REGLA_BULLET_RE = re.compile(
    r"(?i)^\s*[-*•]\s+(?:\*\*)?Regla(?:\s+RRS)?\s+([^\n*—:]+)",
    re.M,
)
# **Case 92** / **CASE 13**
_CASE_MARKDOWN_RE = re.compile(r"(?i)\*\*(?:Case|CASE)\s+(\d{1,4})\*\*")


def _dedupe_preserve(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        key = item.lower()
        if key not in seen:
            seen.add(key)
            out.append(item)
    return out


def _split_rule_alternatives(fragment: str) -> list[str]:
    fragment = re.sub(r"(?i)(?:TR\s+)?CALL\s+[A-Z]?\d+[A-Z]?\b.*", "", fragment)
    out: list[str] = []
    for m in _RRS_TOKEN_RE.finditer(fragment):
        token = (m.group(1) or m.group(2)).strip()
        if token and token not in out:
            out.append(token)
    return out


def extract_rrs_rules(text: str) -> list[str]:
    found: list[str] = []
    for block in _RRS_BLOCK_RE.finditer(text):
        found.extend(_split_rule_alternatives(block.group(1)))
    for m in _RULE_EN_RE.finditer(text):
        found.append(m.group(1))
    for m in _REGLA_MARKDOWN_RE.finditer(text):
        label = m.group(1).strip().rstrip(":")
        found.extend(_split_rule_alternatives(label))
    for m in _REGLA_BULLET_RE.finditer(text):
        label = m.group(1).strip().rstrip(":")
        found.extend(_split_rule_alternatives(label))
    return _dedupe_preserve(found)


def extract_calls(text: str) -> list[str]:
    out: list[str] = []
    for m in _CALL_RE.finditer(text):
        out.append(m.group(1).upper())
    return _dedupe_preserve(out)


def extract_cases(text: str) -> list[str]:
    out: list[str] = []
    for m in _CASE_RE.finditer(text):
        out.append(m.group(1))
    for m in _CASE_MARKDOWN_RE.finditer(text):
        out.append(m.group(1))
    return _dedupe_preserve(out)


def extract_decision(text: str) -> str | None:
    m = _DECISION_RE.search(text)
    if not m:
        return None
    return m.group(1).strip()


def normalize_verdict(decision: str | None) -> str | None:
    if not decision:
        return None
    d = decision.lower()
    if "sin penal" in d or "no penalty" in d:
        return "sin_penalizacion"
    if "exonerar" in d:
        if "penalizar" in d:
            return "mixto"
        return "exonerar"
    if "penalizar" in d:
        return "penalizar"
    return "otro"


def extract_penalized_boats(decision: str | None) -> list[str]:
    if not decision:
        return []
    boats = re.findall(r"(?i)penalizar\s+a\s+([A-Z])", decision)
    return list(dict.fromkeys(b.upper() for b in boats))


def chunk_mentions_rule(text: str, rule: str) -> bool:
    """True si el fragmento parece contener la regla indicada."""
    t = text.lower()
    r = rule.lower()
    if r.startswith("d"):
        patterns = [
            rf"\b{r}\b",
            rf"\bappendix\s+{r[0]}\b",
            rf"\bpart\s+{r[0]}\b",
        ]
    else:
        base = r.split("(")[0]
        patterns = [
            rf"(?i)\bregla\s+{re.escape(r)}\b",
            rf"\brule\s+{re.escape(r)}\b",
            rf"\brule\s+{re.escape(base)}\b",
            rf"\b{re.escape(r)}\b",
        ]
    return any(re.search(p, t) for p in patterns)


def chunk_mentions_case(text: str, case_code: str) -> bool:
    code = case_code.strip()
    if not code:
        return False
    t = text
    if re.search(rf"(?m)^CASE\s+{re.escape(code)}\b", t, re.I):
        return True
    if re.search(rf"\bCase\s+{re.escape(code)}\b", t, re.I):
        return True
    return False


def chunk_mentions_call(text: str, call_code: str) -> bool:
    t = text.upper()
    code = call_code.upper()
    if re.search(rf"\bCALL\s+{re.escape(code)}\b", t):
        return True
    if re.search(rf"\bTR\s+CALL\s+{re.escape(code)}\b", t):
        return True
    # JSONL: chunk_id call|A3; evitar falsos positivos de diagramas (B1, Y2)
    if re.search(rf"(?m)^TR\s+CALL\s+{re.escape(code)}\b", t):
        return True
    return False


def answer_citations(text: str) -> dict[str, list[str]]:
    return {
        "rrs_rules": extract_rrs_rules(text),
        "calls": extract_calls(text),
        "cases": extract_cases(text),
    }
