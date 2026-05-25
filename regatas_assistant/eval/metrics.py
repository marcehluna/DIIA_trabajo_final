"""Métricas de recuperación y de respuesta para el golden set."""

from __future__ import annotations

import re
from typing import Any

from regatas_assistant.eval.refs import (
    answer_citations,
    chunk_mentions_call,
    chunk_mentions_rule,
    extract_penalized_boats,
    normalize_verdict,
)
from regatas_assistant.ingestion import TextChunk

_TOKEN_RE = re.compile(r"[a-zA-ZáéíóúñÁÉÍÓÚÑ]{3,}")


def _tokens(text: str) -> set[str]:
    return {t.lower() for t in _TOKEN_RE.findall(text)}


def _jaccard(a: set[str], b: set[str]) -> float | None:
    if not a and not b:
        return None
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _precision_recall_f1(expected: list[str], predicted: list[str]) -> dict[str, float | None]:
    exp = {x.lower() for x in expected}
    pred = {x.lower() for x in predicted}
    if not exp and not pred:
        return {"precision": None, "recall": None, "f1": None}
    if not pred:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}
    if not exp:
        return {"precision": 0.0, "recall": None, "f1": None}
    tp = len(exp & pred)
    precision = tp / len(pred)
    recall = tp / len(exp)
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    return {"precision": precision, "recall": recall, "f1": f1}


def recall_at_k_rules(
    expected_rules: list[str],
    retrieved: list[TextChunk],
    k: int,
) -> float | None:
    if not expected_rules:
        return None
    top = retrieved[:k]
    hits = 0
    for rule in expected_rules:
        if any(chunk_mentions_rule(c.text, rule) for c in top):
            hits += 1
    return hits / len(expected_rules)


def recall_at_k_calls(
    expected_calls: list[str],
    retrieved: list[TextChunk],
    k: int,
) -> float | None:
    if not expected_calls:
        return None
    top = retrieved[:k]
    hits = 0
    for call in expected_calls:
        if any(chunk_mentions_call(c.text, call) for c in top):
            hits += 1
    return hits / len(expected_calls)


def _chunk_to_dict(c: TextChunk) -> dict[str, Any]:
    return {
        "chunk_id": c.chunk_id(),
        "source_file": c.source_file,
        "page_start": c.page_start,
        "chunk_index": c.chunk_index,
        "doc_type": c.doc_type,
        "ref_id": c.ref_id,
        "header": c.header_line(),
        "text": c.text,
    }


def score_case(
    *,
    expected: dict[str, Any],
    retrieved: list[TextChunk],
    answer: str | None,
    top_k: int,
    output_ideal: str | None = None,
) -> dict[str, Any]:
    """Calcula métricas por caso."""
    exp_rules = expected.get("rrs_rules") or []
    exp_calls = expected.get("calls") or []
    exp_cases = expected.get("cases") or []

    retrieval = {
        "recall_at_k_rules": recall_at_k_rules(exp_rules, retrieved, top_k),
        "recall_at_k_calls": recall_at_k_calls(exp_calls, retrieved, top_k),
        "n_retrieved": len(retrieved),
    }

    response: dict[str, Any] = {}
    if answer is None:
        return {"retrieval": retrieval, "response": response, "retrieved": [_chunk_to_dict(c) for c in retrieved]}

    cites = answer_citations(answer)
    response["citation_rrs"] = _precision_recall_f1(exp_rules, cites["rrs_rules"])
    response["citation_calls"] = _precision_recall_f1(exp_calls, cites["calls"])
    response["citation_cases"] = _precision_recall_f1(exp_cases, cites["cases"])
    response["citations_found"] = cites

    ctx_text = "\n\n".join(c.text for c in retrieved)
    response["token_jaccard_answer_context"] = _jaccard(_tokens(answer), _tokens(ctx_text))
    if output_ideal:
        response["token_jaccard_answer_reference"] = _jaccard(
            _tokens(answer), _tokens(output_ideal)
        )

    exp_verdict = expected.get("verdict")
    ans_decision = None
    for line in answer.splitlines():
        if re.search(r"(?i)dictamen|decisi[oó]n|resoluci[oó]n", line):
            ans_decision = line
            break
    ans_verdict = normalize_verdict(ans_decision or answer[-400:])
    response["verdict_expected"] = exp_verdict
    response["verdict_predicted"] = ans_verdict
    response["verdict_match"] = (
        exp_verdict == ans_verdict if exp_verdict and ans_verdict else None
    )

    exp_boats = set(expected.get("penalized_boats") or [])
    pred_boats = set(extract_penalized_boats(answer))
    if exp_boats or pred_boats:
        response["penalized_boats_match"] = exp_boats == pred_boats if exp_boats else None

    return {
        "retrieval": retrieval,
        "response": response,
        "retrieved": [_chunk_to_dict(c) for c in retrieved],
    }


def _mean(values: list[float | None]) -> float | None:
    nums = [v for v in values if v is not None]
    if not nums:
        return None
    return sum(nums) / len(nums)


def aggregate_metrics(case_results: list[dict[str, Any]]) -> dict[str, Any]:
    """Promedios sobre casos (ignora None donde no aplica)."""
    r_rules = []
    r_calls = []
    f1_rrs = []
    f1_calls = []
    j_ctx = []
    j_ref = []
    verdict_ok = []
    for cr in case_results:
        m = cr.get("metrics") or {}
        ret = m.get("retrieval") or {}
        resp = m.get("response") or {}
        if ret.get("recall_at_k_rules") is not None:
            r_rules.append(ret["recall_at_k_rules"])
        if ret.get("recall_at_k_calls") is not None:
            r_calls.append(ret["recall_at_k_calls"])
        cit = resp.get("citation_rrs") or {}
        if cit.get("f1") is not None:
            f1_rrs.append(cit["f1"])
        cit_c = resp.get("citation_calls") or {}
        if cit_c.get("f1") is not None:
            f1_calls.append(cit_c["f1"])
        if resp.get("token_jaccard_answer_context") is not None:
            j_ctx.append(resp["token_jaccard_answer_context"])
        if resp.get("token_jaccard_answer_reference") is not None:
            j_ref.append(resp["token_jaccard_answer_reference"])
        if resp.get("verdict_match") is not None:
            verdict_ok.append(1.0 if resp["verdict_match"] else 0.0)

    return {
        "n_cases": len(case_results),
        "mean_recall_at_k_rules": _mean(r_rules),
        "mean_recall_at_k_calls": _mean(r_calls),
        "mean_citation_f1_rrs": _mean(f1_rrs),
        "mean_citation_f1_calls": _mean(f1_calls),
        "mean_token_jaccard_answer_context": _mean(j_ctx),
        "mean_token_jaccard_answer_reference": _mean(j_ref),
        "verdict_accuracy": _mean(verdict_ok),
    }
