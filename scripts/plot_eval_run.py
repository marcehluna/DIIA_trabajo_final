#!/usr/bin/env python3
"""Gráficos de métricas a partir de eval/runs/<run>/report.json."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def _resolve_report(path: Path) -> Path:
    return path / "report.json" if path.is_dir() else path


def _val(case: dict, *keys: str, default: float = 0.0) -> float:
    d = case
    for k in keys:
        d = d.get(k) if isinstance(d, dict) else None
        if d is None:
            return default
    if d is None:
        return default
    return float(d)


def _plot_per_case_bars(
    cases: list[dict],
    metric_fn,
    title: str,
    ylabel: str,
    out_path: Path,
    ylim: tuple[float, float] = (0, 1.05),
) -> None:
    ids = [c["id"] for c in cases]
    vals = [metric_fn(c) for c in cases]
    x = np.arange(len(ids))
    fig, ax = plt.subplots(figsize=(11, 4.2))
    colors = ["#27ae60" if v >= 0.5 else "#e74c3c" if v > 0 else "#95a5a6" for v in vals]
    ax.bar(x, vals, color=colors, edgecolor="white", width=0.72)
    ax.set_xticks(x)
    ax.set_xticklabels(ids)
    ax.set_xlabel("Caso (ID)")
    ax.set_ylabel(ylabel)
    ax.set_ylim(ylim)
    ax.set_title(title)
    ax.axhline(0.5, color="#34495e", linestyle="--", linewidth=0.8, alpha=0.5)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def _plot_aggregate_summary(agg: dict, label: str, out_path: Path) -> None:
    keys = [
        ("mean_recall_at_k_rules", "Recall@k reglas"),
        ("mean_recall_at_k_calls", "Recall@k CALL"),
        ("mean_citation_f1_rrs", "F1 citas RRS"),
        ("mean_citation_f1_calls", "F1 citas CALL"),
        ("mean_token_jaccard_answer_context", "Jaccard resp↔contexto"),
        ("mean_token_jaccard_answer_reference", "Jaccard resp↔referencia"),
        ("verdict_accuracy", "Acierto dictamen"),
    ]
    labels: list[str] = []
    vals: list[float] = []
    for key, lab in keys:
        v = agg.get(key)
        if v is not None:
            labels.append(lab)
            vals.append(float(v))

    if not labels:
        return

    fig, ax = plt.subplots(figsize=(9, max(3.5, 0.45 * len(labels))))
    y = np.arange(len(labels))
    colors = ["#2980b9" if v >= 0.5 else "#e67e22" if v > 0 else "#bdc3c7" for v in vals]
    ax.barh(y, vals, color=colors, height=0.55, edgecolor="white")
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlim(0, 1.05)
    ax.set_xlabel("Valor (0–1)")
    ax.set_title(f"Métricas agregadas — {label}")
    for i, v in enumerate(vals):
        ax.text(v + 0.02, i, f"{v:.2f}", va="center", fontsize=8)
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def _plot_metrics_heatmap(cases: list[dict], out_path: Path) -> None:
    rows = []
    row_labels = []
    col_labels = [
        "Recall reglas",
        "Recall CALL",
        "F1 RRS",
        "F1 CALL",
        "Jaccard ctx",
        "Jaccard ref",
        "Dictamen",
    ]

    for c in cases:
        m = c.get("metrics") or {}
        ret = m.get("retrieval") or {}
        resp = m.get("response") or {}
        cit_r = resp.get("citation_rrs") or {}
        cit_c = resp.get("citation_calls") or {}
        vm = resp.get("verdict_match")

        def g(x):
            return np.nan if x is None else float(x)

        rows.append(
            [
                g(ret.get("recall_at_k_rules")),
                g(ret.get("recall_at_k_calls")),
                g(cit_r.get("f1")),
                g(cit_c.get("f1")),
                g(resp.get("token_jaccard_answer_context")),
                g(resp.get("token_jaccard_answer_reference")),
                g(1.0 if vm else 0.0 if vm is False else np.nan),
            ]
        )
        row_labels.append(str(c["id"]))

    data = np.array(rows, dtype=float)
    fig, ax = plt.subplots(figsize=(10, max(4, 0.35 * len(row_labels))))
    im = ax.imshow(data, aspect="auto", cmap="RdYlGn", vmin=0, vmax=1)
    ax.set_xticks(np.arange(len(col_labels)))
    ax.set_xticklabels(col_labels, rotation=35, ha="right", fontsize=8)
    ax.set_yticks(np.arange(len(row_labels)))
    ax.set_yticklabels(row_labels)
    ax.set_title("Mapa de métricas por caso")
    fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_report(report_path: Path, out_dir: Path | None = None) -> Path:
    """Genera PNGs y devuelve la carpeta de salida."""
    report_path = _resolve_report(report_path)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    cases = report.get("cases") or []
    agg = report.get("aggregate") or {}
    label = report.get("label") or report.get("run_id") or "corrida"

    out_dir = out_dir or (report_path.parent / "plots")
    out_dir.mkdir(parents=True, exist_ok=True)

    _plot_per_case_bars(
        cases,
        lambda c: _val(c, "metrics", "retrieval", "recall_at_k_rules"),
        f"Recall@k — reglas RRS ({label})",
        "Recall",
        out_dir / "01_recall_reglas_por_caso.png",
    )
    _plot_per_case_bars(
        cases,
        lambda c: _val(c, "metrics", "retrieval", "recall_at_k_calls"),
        f"Recall@k — TR CALL ({label})",
        "Recall",
        out_dir / "02_recall_calls_por_caso.png",
    )
    _plot_per_case_bars(
        cases,
        lambda c: _val(c, "metrics", "response", "citation_rrs", "f1"),
        f"F1 citas RRS en respuesta ({label})",
        "F1",
        out_dir / "03_f1_citas_rrs_por_caso.png",
    )
    _plot_per_case_bars(
        cases,
        lambda c: _val(c, "metrics", "response", "citation_calls", "f1"),
        f"F1 citas CALL en respuesta ({label})",
        "F1",
        out_dir / "04_f1_citas_calls_por_caso.png",
    )
    _plot_per_case_bars(
        cases,
        lambda c: _val(c, "metrics", "response", "token_jaccard_answer_context"),
        f"Jaccard respuesta ↔ contexto ({label})",
        "Jaccard",
        out_dir / "05_jaccard_respuesta_contexto.png",
    )
    _plot_per_case_bars(
        cases,
        lambda c: _val(c, "metrics", "response", "token_jaccard_answer_reference"),
        f"Jaccard respuesta ↔ output ideal ({label})",
        "Jaccard",
        out_dir / "06_jaccard_respuesta_referencia.png",
    )
    _plot_aggregate_summary(agg, label, out_dir / "07_metricas_agregadas.png")
    _plot_metrics_heatmap(cases, out_dir / "08_heatmap_metricas.png")

    return out_dir


def main() -> None:
    p = argparse.ArgumentParser(description="Gráficos de una corrida de evaluación")
    p.add_argument("report", type=Path, help="report.json o carpeta de corrida")
    p.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Carpeta de salida (default: <corrida>/plots)",
    )
    args = p.parse_args()
    out = plot_report(args.report, args.out_dir)
    print(f"Gráficos guardados en: {out}")
    for f in sorted(out.glob("*.png")):
        print(f"  - {f.name}")


if __name__ == "__main__":
    main()
