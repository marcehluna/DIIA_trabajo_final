"""Exportación CSV de faithfulness por caso y por afirmación."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


CASE_FIELDS = [
    "eval_id",
    "run_id",
    "label",
    "case_id",
    "titulo",
    "has_answer",
    "n_claims",
    "n_supported",
    "n_not_supported",
    "n_unknown",
    "n_parse_failures",
    "faithfulness_rate",
    "faithfulness_rate_strict",
    "recall_at_k_rules",
    "recall_at_k_calls",
    "f1_citation_rrs",
    "f1_citation_calls",
    "verdict_match",
]

CLAIM_FIELDS = [
    "eval_id",
    "run_id",
    "label",
    "case_id",
    "claim_index",
    "claim",
    "verdict",
    "evidence_ids",
    "rationale",
]


def _eval_id_for_run(run_id: str, diario_path: Path | None) -> str:
    if not diario_path or not diario_path.is_file():
        return ""
    try:
        data = json.loads(diario_path.read_text(encoding="utf-8"))
        return (data.get("runs") or {}).get(run_id, "")
    except (json.JSONDecodeError, OSError):
        return ""


def _case_row(
    report: dict[str, Any],
    case: dict[str, Any],
    *,
    eval_id: str = "",
) -> dict[str, Any]:
    run_id = report.get("run_id") or ""
    label = report.get("label") or ""
    cid = case.get("id")
    metrics = case.get("metrics") or {}
    ret = metrics.get("retrieval") or {}
    resp = metrics.get("response") or {}
    fh = resp.get("faithfulness") or {}
    cit = resp.get("citation_rrs") or {}
    cit_c = resp.get("citation_calls") or {}

    return {
        "eval_id": eval_id,
        "run_id": run_id,
        "label": label,
        "case_id": cid,
        "titulo": (case.get("titulo") or "").strip(),
        "has_answer": bool(case.get("answer")),
        "n_claims": fh.get("n_claims"),
        "n_supported": fh.get("n_supported"),
        "n_not_supported": fh.get("n_not_supported"),
        "n_unknown": fh.get("n_unknown"),
        "n_parse_failures": fh.get("n_parse_failures"),
        "faithfulness_rate": fh.get("faithfulness_rate"),
        "faithfulness_rate_strict": fh.get("faithfulness_rate_strict"),
        "recall_at_k_rules": ret.get("recall_at_k_rules"),
        "recall_at_k_calls": ret.get("recall_at_k_calls"),
        "f1_citation_rrs": cit.get("f1"),
        "f1_citation_calls": cit_c.get("f1"),
        "verdict_match": resp.get("verdict_match"),
    }


def _claim_rows(
    report: dict[str, Any],
    case: dict[str, Any],
    *,
    eval_id: str = "",
) -> list[dict[str, Any]]:
    run_id = report.get("run_id") or ""
    label = report.get("label") or ""
    cid = case.get("id")
    fh = (case.get("metrics") or {}).get("response", {}).get("faithfulness") or {}
    claims = fh.get("claims") or []
    rows: list[dict[str, Any]] = []
    for i, row in enumerate(claims, start=1):
        if not isinstance(row, dict):
            continue
        ids = row.get("evidence_ids") or []
        rows.append(
            {
                "eval_id": eval_id,
                "run_id": run_id,
                "label": label,
                "case_id": cid,
                "claim_index": i,
                "claim": (row.get("claim") or "").strip(),
                "verdict": row.get("verdict"),
                "evidence_ids": "|".join(str(x) for x in ids),
                "rationale": (row.get("rationale") or "").strip(),
            }
        )
    return rows


def export_faithfulness_csv(
    report: dict[str, Any],
    out_dir: Path,
    *,
    diario_path: Path | None = None,
) -> tuple[Path, Path]:
    """Escribe faithfulness_by_case.csv y faithfulness_claims_detail.csv en out_dir."""
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    eval_id = _eval_id_for_run(
        report.get("run_id") or "",
        diario_path,
    )

    case_rows = [_case_row(report, c, eval_id=eval_id) for c in report.get("cases") or []]
    claim_rows: list[dict[str, Any]] = []
    for c in report.get("cases") or []:
        claim_rows.extend(_claim_rows(report, c, eval_id=eval_id))

    by_case_path = out_dir / "faithfulness_by_case.csv"
    claims_path = out_dir / "faithfulness_claims_detail.csv"

    with by_case_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CASE_FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(case_rows)

    with claims_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CLAIM_FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(claim_rows)

    return by_case_path, claims_path


def export_combined_by_case(
    reports: list[dict[str, Any]],
    out_path: Path,
    *,
    diario_path: Path | None = None,
) -> Path:
    """Un CSV con una fila por (eval_id, case_id) por cada corrida."""
    rows: list[dict[str, Any]] = []
    for report in reports:
        eval_id = _eval_id_for_run(report.get("run_id") or "", diario_path)
        for case in report.get("cases") or []:
            rows.append(_case_row(report, case, eval_id=eval_id))

    out_path = out_path.resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CASE_FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    return out_path


def export_comparison_wide(
    reports: list[dict[str, Any]],
    out_path: Path,
    *,
    diario_path: Path | None = None,
) -> Path:
    """Una fila por case_id con columnas E0_* y E12_* de faithfulness."""
    by_eval: dict[str, dict[str, Any]] = {}
    for report in reports:
        eid = _eval_id_for_run(report.get("run_id") or "", diario_path) or report.get(
            "label", ""
        )
        for case in report.get("cases") or []:
            cid = str(case.get("id"))
            by_eval.setdefault(cid, {"case_id": cid, "titulo": case.get("titulo") or ""})
            row = _case_row(report, case, eval_id=eid)
            prefix = eid or report.get("label", "run")
            for key in (
                "faithfulness_rate",
                "faithfulness_rate_strict",
                "n_claims",
                "n_supported",
                "n_unknown",
            ):
                by_eval[cid][f"{prefix}_{key}"] = row.get(key)

    fieldnames = ["case_id", "titulo"]
    if reports:
        prefixes = []
        for report in reports:
            eid = _eval_id_for_run(report.get("run_id") or "", diario_path) or report.get(
                "label", "run"
            )
            if eid not in prefixes:
                prefixes.append(eid)
        for p in prefixes:
            for key in (
                "faithfulness_rate",
                "faithfulness_rate_strict",
                "n_claims",
                "n_supported",
                "n_unknown",
            ):
                fieldnames.append(f"{p}_{key}")

    out_path = out_path.resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for cid in sorted(by_eval.keys(), key=lambda x: int(x) if x.isdigit() else x):
            w.writerow(by_eval[cid])
    return out_path
