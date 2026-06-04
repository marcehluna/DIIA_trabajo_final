#!/usr/bin/env python3
"""Barrido faithfulness (todos los casos) en E0 + E12 y exporta CSV."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from regatas_assistant.eval.faithfulness_csv import (  # noqa: E402
    export_combined_by_case,
    export_comparison_wide,
    export_faithfulness_csv,
)

sys.path.insert(0, str(ROOT / "scripts"))
from score_faithfulness import score_run_dir  # noqa: E402

DEFAULT_RUNS = (
    ("E0", ROOT / "eval" / "corrida baseline"),
    ("E12", ROOT / "eval" / "runs" / "20260603_183901_prompt_v2_cot"),
)
DIARIO = ROOT / "eval" / "diario_runs.json"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--skip-score",
        action="store_true",
        help="Solo exportar CSV desde report.json existente (sin LLM)",
    )
    p.add_argument("--model", default=None)
    p.add_argument("--max-claims", type=int, default=24)
    p.add_argument("--verify-batch-size", type=int, default=6)
    args = p.parse_args()

    reports: list[dict] = []
    for tag, run_dir in DEFAULT_RUNS:
        if not (run_dir / "report.json").is_file():
            print(f"ERROR: falta report.json en {run_dir} ({tag})")
            return 1
        print(f"\n========== {tag}: {run_dir.name} ==========", flush=True)
        if args.skip_score:
            import json

            report = json.loads(
                (run_dir / "report.json").read_text(encoding="utf-8")
            )
        else:
            report = score_run_dir(
                run_dir,
                model=args.model,
                max_claims=args.max_claims,
                verify_batch_size=args.verify_batch_size,
                case_ids=None,
                dry_run=False,
            )

        by_case, claims = export_faithfulness_csv(
            report, run_dir, diario_path=DIARIO
        )
        print(f"  CSV caso:   {by_case}")
        print(f"  CSV claims: {claims}")
        reports.append(report)

    combined = export_combined_by_case(
        reports,
        ROOT / "eval" / "faithfulness_all_runs_by_case.csv",
        diario_path=DIARIO,
    )
    wide = export_comparison_wide(
        reports,
        ROOT / "eval" / "faithfulness_e0_e12_comparison.csv",
        diario_path=DIARIO,
    )
    print(f"\n=== Barrido completo ===")
    print(f"Combinado (todas las filas): {combined}")
    print(f"Comparación ancha E0 vs E12:  {wide}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
