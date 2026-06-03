"""Faithfulness (fidelidad): cada afirmación de la respuesta vs contexto recuperado.

Usa un LLM como juez en dos pasos:
1. Extraer afirmaciones atómicas verificables de la respuesta.
2. Verificar si cada una está respaldada por los fragmentos recuperados.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from regatas_assistant.llm.base import LLMClient

logger = logging.getLogger(__name__)


class _ModelOverrideLLM(LLMClient):
    """Delega en un cliente HTTP permitiendo fijar el modelo por llamada."""

    def __init__(self, base: LLMClient, model: str):
        self._base = base
        self._model = model

    def complete(self, system_prompt: str, user_content: str) -> str:
        return self._base.complete(
            system_prompt, user_content, model=self._model
        )


def llm_for_judge(llm: LLMClient, model: str | None) -> LLMClient:
    if model:
        return _ModelOverrideLLM(llm, model)
    return llm


_MAX_CLAIMS = 24
_MAX_CONTEXT_CHARS = 14_000
_VERIFY_BATCH_SIZE = 6
_MAX_LLM_RETRIES = 2

_JSON_RETRY_SUFFIX = (
    "\n\nIMPORTANTE: Respondé solo con JSON válido, sin markdown ni texto extra."
)

_EXTRACT_SYSTEM = """Sos un evaluador de RAG para protestas náuticas (RRS, Call Book, Case Book).
Tu tarea es listar afirmaciones verificables de una respuesta del asistente.

Reglas:
- Incluí solo hechos, normas citadas, interpretaciones y conclusiones del dictamen.
- NO incluyas encabezados de sección, viñetas vacías ni frases puramente introductorias.
- Cada ítem debe ser una sola afirmación atómica (una idea).
- Máximo {max_claims} ítems.
- Respondé ÚNICAMENTE con JSON válido, sin ``` ni comentarios:
{{"claims": ["afirmación 1", "afirmación 2"]}}"""

_VERIFY_SYSTEM = """Sos un evaluador de fidelidad (faithfulness) en RAG náutico.
Para cada afirmación, decidí si está respaldada por los fragmentos de evidencia dados.

Veredictos (usá exactamente estas palabras en minúsculas):
- supported
- not_supported
- unknown

Reglas:
- Solo podés usar el texto de evidencia; no conocimiento externo.
- Si la afirmación cita una regla/call/caso, debe aparecer o deducirse del fragmento.
- Respondé ÚNICAMENTE con JSON válido, sin ``` ni comentarios:
{{"results": [{{"claim": "texto igual al input", "verdict": "supported", "evidence_ids": ["id"], "rationale": "breve"}}]}}"""

_VERIFY_ONE_SYSTEM = """Sos un evaluador de fidelidad en RAG náutico.
Decidí si UNA afirmación está respaldada por los fragmentos de evidencia.

Veredicto (exactamente uno): supported | not_supported | unknown
Solo usá la evidencia dada.

Respondé ÚNICAMENTE con JSON válido, sin ```:
{{"verdict": "supported", "evidence_ids": ["chunk_id"], "rationale": "breve"}}"""


def _strip_code_fences(raw: str) -> str:
    text = (raw or "").strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text, re.I)
    if fence:
        return fence.group(1).strip()
    return text


def _repair_json_text(raw: str) -> str:
    """Limpiezas comunes en JSON generado por LLM."""
    s = raw.strip()
    s = re.sub(r",\s*([}\]])", r"\1", s)
    s = re.sub(r"(?<!\\)'", '"', s)
    return s


def _extract_balanced_json(raw: str) -> str | None:
    start = raw.find("{")
    if start < 0:
        return None
    depth = 0
    in_str = False
    escape = False
    for i in range(start, len(raw)):
        ch = raw[i]
        if in_str:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return raw[start : i + 1]
    return None


def _parse_json_payload(text: str) -> Any | None:
    raw = _strip_code_fences(text)
    if not raw:
        return None

    candidates: list[str] = [raw]
    balanced = _extract_balanced_json(raw)
    if balanced and balanced not in candidates:
        candidates.append(balanced)
    repaired = _repair_json_text(raw)
    if repaired not in candidates:
        candidates.append(repaired)
    if balanced:
        rep_bal = _repair_json_text(balanced)
        if rep_bal not in candidates:
            candidates.append(rep_bal)

    for candidate in candidates:
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue

    partial = _parse_results_loose(raw)
    if partial is not None:
        return partial
    return None


def _parse_results_loose(raw: str) -> dict[str, Any] | None:
    """Intenta recuperar filas results[] de JSON truncado o con ruido."""
    rows: list[dict[str, Any]] = []
    block_re = re.compile(
        r'\{\s*"claim"\s*:\s*"(?P<claim>(?:\\.|[^"\\])*)"\s*,\s*'
        r'"verdict"\s*:\s*"(?P<verdict>[^"]+)"',
        re.I | re.S,
    )
    for m in block_re.finditer(raw):
        claim = m.group("claim").replace('\\"', '"')
        rows.append(
            {
                "claim": claim,
                "verdict": m.group("verdict").strip().lower(),
                "evidence_ids": [],
                "rationale": "",
            }
        )
    if rows:
        return {"results": rows}
    return None


def _llm_json(
    llm: LLMClient,
    system: str,
    user: str,
    *,
    retries: int = _MAX_LLM_RETRIES,
) -> tuple[Any | None, str]:
    """Llama al LLM y parsea JSON; reintenta con recordatorio si falla."""
    last_raw = ""
    prompt = system
    for attempt in range(retries + 1):
        last_raw = llm.complete(prompt, user)
        data = _parse_json_payload(last_raw)
        if data is not None:
            return data, last_raw
        if attempt < retries:
            prompt = system + _JSON_RETRY_SUFFIX
            user = (
                user
                + "\n\nTu respuesta anterior no fue JSON válido. "
                "Repetí solo el objeto JSON requerido."
            )
    return None, last_raw


def _format_evidence(chunks: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    total = 0
    for i, ch in enumerate(chunks, start=1):
        cid = ch.get("chunk_id") or f"chunk_{i}"
        header = ch.get("header") or ch.get("source_file") or ""
        text = (ch.get("text") or "").strip()
        block = f"[{i}] id={cid}\n{header}\n{text}\n"
        if total + len(block) > _MAX_CONTEXT_CHARS:
            block = block[: max(0, _MAX_CONTEXT_CHARS - total)]
            parts.append(block)
            break
        parts.append(block)
        total += len(block)
    return "\n---\n".join(parts)


def extract_claims(llm: LLMClient, answer: str, *, max_claims: int = _MAX_CLAIMS) -> list[str]:
    if not (answer or "").strip():
        return []
    system = _EXTRACT_SYSTEM.format(max_claims=max_claims)
    user = f"Respuesta del asistente:\n\n{answer.strip()}"
    data, raw = _llm_json(llm, system, user)
    if data is None:
        logger.warning("faithfulness: no se parsearon claims; raw=%s", raw[:400])
        return _extract_claims_fallback(raw)
    if not isinstance(data, dict):
        return []
    claims = data.get("claims")
    if not isinstance(claims, list):
        return []
    out: list[str] = []
    for c in claims:
        if isinstance(c, str) and c.strip():
            out.append(c.strip())
        if len(out) >= max_claims:
            break
    return out


def _extract_claims_fallback(raw: str) -> list[str]:
    """Lista numerada o viñetas si el JSON de claims falló."""
    lines: list[str] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        m = re.match(r'^[\d\-*•]+\s*["\']?(.+?)["\']?\s*,?\s*$', line)
        if m and len(m.group(1)) > 12:
            lines.append(m.group(1).strip())
    return lines[:_MAX_CLAIMS]


def _verify_batch(
    llm: LLMClient,
    claims: list[str],
    evidence: str,
) -> list[dict[str, Any]] | None:
    claims_json = json.dumps(claims, ensure_ascii=False, indent=2)
    user = (
        f"Afirmaciones a verificar (repetí cada claim textualmente en la salida):\n"
        f"{claims_json}\n\n"
        f"Fragmentos de evidencia (solo estos son válidos):\n\n{evidence}"
    )
    data, raw = _llm_json(llm, _VERIFY_SYSTEM, user)
    if data is None:
        logger.debug("faithfulness: batch verify parse fail; raw=%s", raw[:500])
        return None
    return _rows_from_verify_payload(data, claims)


def _rows_from_verify_payload(
    data: Any,
    expected_claims: list[str],
) -> list[dict[str, Any]] | None:
    if not isinstance(data, dict):
        return None
    results = data.get("results")
    if not isinstance(results, list):
        return None

    by_claim: dict[str, dict[str, Any]] = {}
    ordered: list[dict[str, Any]] = []
    for row in results:
        if not isinstance(row, dict):
            continue
        norm = _normalize_verdict_row(row)
        claim_key = norm["claim"].lower()
        if claim_key:
            by_claim[claim_key] = norm
        ordered.append(norm)

    if len(expected_claims) == len(ordered) and not by_claim:
        return ordered

    out: list[dict[str, Any]] = []
    for i, c in enumerate(expected_claims):
        row = by_claim.get(c.lower())
        if row is None and i < len(ordered):
            row = ordered[i]
            if row.get("claim", "").lower() != c.lower():
                row = {**row, "claim": c}
        out.append(row if row else _fallback_result(c, reason="sin fila en results"))
    return out


def _verify_one(
    llm: LLMClient,
    claim: str,
    evidence: str,
) -> dict[str, Any]:
    user = (
        f"Afirmación:\n{claim}\n\n"
        f"Fragmentos de evidencia:\n\n{evidence}"
    )
    data, raw = _llm_json(llm, _VERIFY_ONE_SYSTEM, user, retries=1)
    if isinstance(data, dict) and data.get("verdict"):
        return _normalize_verdict_row({**data, "claim": claim})
    loose = _parse_json_payload(raw)
    if isinstance(loose, dict) and loose.get("verdict"):
        return _normalize_verdict_row({**loose, "claim": claim})
    return _fallback_result(claim, reason="verify_one: JSON inválido")


def verify_claims(
    llm: LLMClient,
    claims: list[str],
    chunks: list[dict[str, Any]],
    *,
    batch_size: int = _VERIFY_BATCH_SIZE,
) -> list[dict[str, Any]]:
    if not claims:
        return []
    evidence = _format_evidence(chunks)
    out: list[dict[str, Any]] = []
    bs = max(1, batch_size)

    for start in range(0, len(claims), bs):
        batch = claims[start : start + bs]
        rows = _verify_batch(llm, batch, evidence)
        if rows is not None and len(rows) == len(batch):
            out.extend(rows)
            continue
        for claim in batch:
            out.append(_verify_one(llm, claim, evidence))
    return out


def _normalize_verdict_row(row: dict[str, Any]) -> dict[str, Any]:
    verdict = str(row.get("verdict") or "unknown").lower().strip()
    verdict = re.sub(r"[^a-z_]", "", verdict.replace(" ", "_"))
    if verdict not in ("supported", "not_supported", "unknown"):
        if verdict in ("yes", "true", "si", "sí", "support", "supported_yes"):
            verdict = "supported"
        elif verdict in ("no", "false", "unsupported", "notsupported", "refuted"):
            verdict = "not_supported"
        else:
            verdict = "unknown"
    ids = row.get("evidence_ids") or row.get("evidence_chunk_ids") or []
    if not isinstance(ids, list):
        ids = []
    return {
        "claim": (row.get("claim") or "").strip(),
        "verdict": verdict,
        "evidence_ids": [str(x) for x in ids if x],
        "rationale": (row.get("rationale") or "").strip(),
    }


def _fallback_result(claim: str, *, reason: str = "") -> dict[str, Any]:
    return {
        "claim": claim,
        "verdict": "unknown",
        "evidence_ids": [],
        "rationale": reason or "No se pudo parsear la verificación del juez.",
    }


def summarize_faithfulness(
    verified: list[dict[str, Any]],
    *,
    parse_failures: int = 0,
) -> dict[str, Any]:
    n = len(verified)
    if n == 0:
        return {
            "n_claims": 0,
            "n_supported": 0,
            "n_not_supported": 0,
            "n_unknown": 0,
            "n_parse_failures": parse_failures,
            "faithfulness_rate": None,
            "faithfulness_rate_strict": None,
            "claims": [],
        }
    supported = sum(1 for r in verified if r.get("verdict") == "supported")
    not_sup = sum(1 for r in verified if r.get("verdict") == "not_supported")
    unknown = sum(1 for r in verified if r.get("verdict") == "unknown")
    strict_denom = supported + not_sup
    return {
        "n_claims": n,
        "n_supported": supported,
        "n_not_supported": not_sup,
        "n_unknown": unknown,
        "n_parse_failures": parse_failures,
        "faithfulness_rate": supported / n,
        "faithfulness_rate_strict": (
            supported / strict_denom if strict_denom else None
        ),
        "claims": verified,
    }


def score_faithfulness(
    llm: LLMClient,
    answer: str | None,
    retrieved: list[dict[str, Any]],
    *,
    max_claims: int = _MAX_CLAIMS,
    verify_batch_size: int = _VERIFY_BATCH_SIZE,
) -> dict[str, Any]:
    """Calcula faithfulness para un caso. `retrieved` = lista de dicts chunk."""
    if not answer or not (answer or "").strip():
        return summarize_faithfulness([])
    chunks = retrieved or []
    claims = extract_claims(llm, answer, max_claims=max_claims)
    verified = verify_claims(
        llm, claims, chunks, batch_size=verify_batch_size
    )
    parse_failures = sum(
        1
        for r in verified
        if "parse" in (r.get("rationale") or "").lower()
        or "inválido" in (r.get("rationale") or "").lower()
    )
    return summarize_faithfulness(verified, parse_failures=parse_failures)
