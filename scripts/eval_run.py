#!/usr/bin/env python3
"""Ejecuta una corrida de evaluación sobre el golden set y guarda resultados."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from regatas_assistant.eval.runner import EvalRunConfig, run_evaluation  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser(description="Correr evaluación RAG (golden set)")
    p.add_argument(
        "--label",
        required=True,
        help="Etiqueta de la corrida (ej. baseline, ingesta_reglas_csv)",
    )
    p.add_argument(
        "--retrieval-only",
        action="store_true",
        help="Solo recuperación; no llama al LLM",
    )
    p.add_argument(
        "--eval-set",
        type=Path,
        default=ROOT / "eval" / "data" / "eval_set.json",
    )
    p.add_argument(
        "--runs-dir",
        type=Path,
        default=ROOT / "eval" / "runs",
    )
    p.add_argument("--lang", choices=("es", "en"), default=None)
    p.add_argument("--strategy", choices=("cot", "few_shot_cot"), default=None)
    p.add_argument("--model", default=None, help="Modelo LLM (backend http)")
    p.add_argument(
        "--plots",
        action="store_true",
        help="Generar gráficos PNG en <corrida>/plots/",
    )
    args = p.parse_args()

    os.environ.setdefault("REGATAS_ACTIVITY_CONSOLE", "0")

    report = run_evaluation(
        EvalRunConfig(
            label=args.label,
            retrieval_only=args.retrieval_only,
            eval_set_path=args.eval_set,
            runs_dir=args.runs_dir,
            system_prompt_lang=args.lang,
            prompt_strategy=args.strategy,
            llm_model=args.model,
        )
    )
    run_dir = args.runs_dir / report["run_id"]
    print(f"Corrida guardada en: {run_dir}")
    print((run_dir / "summary.txt").read_text(encoding="utf-8"))

    import importlib.util

    tbl_path = ROOT / "scripts" / "build_eval_results_table.py"
    spec_tbl = importlib.util.spec_from_file_location("build_eval_results_table", tbl_path)
    mod_tbl = importlib.util.module_from_spec(spec_tbl)
    assert spec_tbl.loader
    spec_tbl.loader.exec_module(mod_tbl)
    mod_tbl.write_comparison_table(run_dir)
    print(f"Tabla comparativa: {run_dir / 'results_comparison.md'}")

    if args.plots:
        import importlib.util

        plot_path = ROOT / "scripts" / "plot_eval_run.py"
        spec = importlib.util.spec_from_file_location("plot_eval_run", plot_path)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader
        spec.loader.exec_module(mod)
        plots_dir = mod.plot_report(run_dir)
        print(f"Gráficos: {plots_dir}")


if __name__ == "__main__":
    main()
