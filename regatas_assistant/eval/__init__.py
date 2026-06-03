"""Evaluación reproducible del pipeline RAG (golden set, métricas, corridas)."""

from regatas_assistant.eval.golden import build_eval_set_from_excel, load_eval_set
from regatas_assistant.eval.faithfulness import score_faithfulness
from regatas_assistant.eval.metrics import aggregate_metrics, score_case
from regatas_assistant.eval.runner import run_evaluation

__all__ = [
    "build_eval_set_from_excel",
    "load_eval_set",
    "score_case",
    "score_faithfulness",
    "aggregate_metrics",
    "run_evaluation",
]
