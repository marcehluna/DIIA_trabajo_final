#!/usr/bin/env python3
"""Calcula faithfulness (LLM-as-judge) sobre una corrida ya guardada."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from regatas_assistant.config import Settings  # noqa: E402
from regatas_assistant.eval.enrich import enrich_report, export_sidecars  # noqa: E402
from regatas_assistant.eval.faithfulness import llm_for_judge, score_faithfulness  # noqa: E402
from regatas_assistant.eval.metrics import aggregate_metrics  # noqa: E402


def _build_llm(settings: Settings):
    from regatas_assistant.llm.chat_http_client import HTTPChatClient
    from regatas_assistant.llm.stub import StubLLMClient

    if settings.llm_backend == "stub":
        raise SystemExit(
            "Faithfulness requiere REGATAS_LLM_BACKEND=http (Ollama u otro host)."
        )
    return HTTPChatClient(settings)


def score_run_dir(
    run_dir: Path,
    *,
    model: str | None = None,
    max_claims: int = 24,
    verify_batch_size: int = 6,
    case_ids: set[str] | None = None,
    dry_run: bool = False,
) -> dict:
    run_dir = run_dir.resolve()
    report_path = run_dir / "report.json"
    if not report_path.is_file():
        raise FileNotFoundError(f"No hay report.json en {run_dir}")

    report = json.loads(report_path.read_text(encoding="utf-8"))
    if report.get("retrieval_only"):
        raise SystemExit("Corrida retrieval-only: no hay respuestas para evaluar.")

    settings = Settings.from_env()
    if model:
        settings.llm_model = model
    llm = llm_for_judge(_build_llm(settings), model)

    cases = report.get("cases") or []
    n = len(cases)
    for i, case in enumerate(cases, start=1):
        cid = str(case.get("id", "?"))
        if case_ids is not None and cid not in case_ids:
            continue
        answer = case.get("answer")
        if not answer:
            continue
        retrieved = (case.get("metrics") or {}).get("retrieved") or []
        titulo = (case.get("titulo") or "")[:40]
        print(f"[{i}/{n}] Caso {cid}: {titulo}…", flush=True)
        if dry_run:
            continue
        fh = score_faithfulness(
            llm,
            answer,
            retrieved,
            max_claims=max_claims,
            verify_batch_size=verify_batch_size,
        )
        case.setdefault("metrics", {}).setdefault("response", {})["faithfulness"] = fh
        rate = fh.get("faithfulness_rate")
        rate_s = f"{rate:.2f}" if rate is not None else "n/a"
        print(
            f"    → {fh.get('n_supported', 0)}/{fh.get('n_claims', 0)} "
            f"supported (rate={rate_s})",
            flush=True,
        )

    if dry_run:
        print("Dry-run: no se escribió report.json")
        return report

    report["aggregate"] = aggregate_metrics(cases)
    report = enrich_report(report)
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    export_sidecars(report, run_dir)

    agg = report.get("aggregate") or {}
    print("\n=== Faithfulness agregado ===")
    print(f"Media:    {agg.get('mean_faithfulness_rate')}")
    print(f"Estricta: {agg.get('mean_faithfulness_rate_strict')}")
    print(f"Actualizado: {report_path}")
    return report


def main() -> None:
    p = argparse.ArgumentParser(description="Faithfulness LLM sobre corrida guardada")
    p.add_argument(
        "run_dir",
        type=Path,
        help="Carpeta con report.json (eval/runs/<id> o eval/corrida baseline)",
    )
    p.add_argument("--model", default=None, help="Modelo juez (default: REGATAS_LLM_MODEL)")
    p.add_argument("--max-claims", type=int, default=24)
    p.add_argument(
        "--verify-batch-size",
        type=int,
        default=6,
        help="Afirmaciones por llamada de verificación (menor = JSON más estable)",
    )
    p.add_argument(
        "--cases",
        default="",
        help="IDs de caso separados por coma (ej. 1,3); vacío = todos",
    )
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    score_run_dir(
        args.run_dir,
        model=args.model,
        max_claims=args.max_claims,
        verify_batch_size=args.verify_batch_size,
        case_ids=_parse_case_ids(args.cases),
        dry_run=args.dry_run,
    )


def _parse_case_ids(raw: str) -> set[str] | None:
    if not (raw or "").strip():
        return None
    return {x.strip() for x in raw.split(",") if x.strip()}


if __name__ == "__main__":
    main()
