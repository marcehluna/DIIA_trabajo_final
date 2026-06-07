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
    p.add_argument(
        "--response-lang",
        choices=("es", "en"),
        default=None,
        help="Idioma del informe (en = salida inglés, E14); default es",
    )
    p.add_argument("--strategy", choices=("cot", "few_shot_cot"), default=None)
    p.add_argument("--model", default=None, help="Modelo LLM (backend http)")
    p.add_argument(
        "--plots",
        action="store_true",
        help="Generar gráficos PNG en <corrida>/plots/",
    )
    p.add_argument(
        "--diario-nota",
        default="",
        help="Nota breve para eval/DIARIO_PRUEBAS.md (qué probaste)",
    )
    p.add_argument(
        "--skip-diario",
        action="store_true",
        help="No actualizar DIARIO_PRUEBAS.md al finalizar",
    )
    p.add_argument(
        "--faithfulness",
        action="store_true",
        help="Medir faithfulness (LLM juez: afirmaciones vs contexto recuperado)",
    )
    p.add_argument(
        "--embedding-backend",
        choices=("lexical", "http", "local", "hybrid"),
        default=None,
        help="Override REGATAS_EMBEDDING_BACKEND (p. ej. hybrid)",
    )
    p.add_argument(
        "--hybrid-semantic-backend",
        choices=("local", "http"),
        default=None,
        help="Rama semántica del híbrido (default: local)",
    )
    args = p.parse_args()

    os.environ.setdefault("REGATAS_ACTIVITY_CONSOLE", "0")

    report = run_evaluation(
        EvalRunConfig(
            label=args.label,
            retrieval_only=args.retrieval_only,
            compute_faithfulness=args.faithfulness,
            faithfulness_model=args.model,
            eval_set_path=args.eval_set,
            runs_dir=args.runs_dir,
            system_prompt_lang=args.lang,
            response_language=args.response_lang,
            prompt_strategy=args.strategy,
            llm_model=args.model,
            embedding_backend=args.embedding_backend,
            hybrid_semantic_backend=args.hybrid_semantic_backend,
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

    _postprocess_run(run_dir, skip_diario=args.skip_diario, diario_nota=args.diario_nota)


def _postprocess_run(run_dir: Path, *, skip_diario: bool, diario_nota: str) -> None:
    """Export CSV retrieval, gráficos agregados, comparación y diario."""
    import importlib.util

    hits = run_dir / "retrieval_hits.json"
    if hits.is_file():
        export_path = ROOT / "scripts" / "export_retrieval_hits_csv.py"
        spec = importlib.util.spec_from_file_location("export_retrieval_hits_csv", export_path)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader
        spec.loader.exec_module(mod)
        try:
            mod.export(hits, run_dir)
        except Exception as e:
            print(f"(Aviso) export_retrieval_hits_csv: {e}")

        agg_path = ROOT / "scripts" / "aggregate_retrieval_hits.py"
        spec2 = importlib.util.spec_from_file_location("aggregate_retrieval_hits", agg_path)
        mod2 = importlib.util.module_from_spec(spec2)
        assert spec2.loader
        spec2.loader.exec_module(mod2)
        try:
            label = run_dir.name.split("_", 2)[-1] if "_" in run_dir.name else run_dir.name
            mod2.process_run(run_dir, label)
            baseline = ROOT / "eval" / "corrida baseline"
            if baseline.is_dir() and baseline != run_dir.resolve():
                rows_a = mod2._read_detail(run_dir / "retrieval_hits_detail.csv")
                agg_a, _, _ = mod2.aggregate_detail(rows_a, label)
                rows_b = mod2._read_detail(baseline / "retrieval_hits_detail.csv")
                agg_b, _, _ = mod2.aggregate_detail(rows_b, "baseline")
                out_cmp = run_dir / "plots_retrieval" / "05_comparacion_corridas.png"
                mod2._plot_compare_runs(agg_a, agg_b, label, "baseline", out_cmp)
                print(f"Comparación retrieval: {out_cmp}")
        except Exception as e:
            print(f"(Aviso) aggregate_retrieval_hits: {e}")

    baseline_dir = ROOT / "eval" / "corrida baseline"
    if baseline_dir.is_dir():
        import subprocess

        print("\n=== Comparación vs baseline (report.json) ===")
        try:
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "compare_eval_runs.py"),
                    str(baseline_dir),
                    str(run_dir),
                ],
                check=False,
                cwd=str(ROOT),
            )
        except Exception as e:
            print(f"(Aviso) compare_eval_runs: {e}")

    if not skip_diario:
        from regatas_assistant.eval.diario import update_diario_after_run

        try:
            diario = update_diario_after_run(run_dir, nota=diario_nota)
            print(f"\nDiario de pruebas: {diario}")
        except Exception as e:
            print(f"(Aviso) update_diario: {e}")


if __name__ == "__main__":
    main()
