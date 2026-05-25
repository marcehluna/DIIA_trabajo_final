#!/usr/bin/env python3
"""Agrega retrieval_hits_detail.csv y genera CSV + gráficos comparables entre corridas."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]

EXPECTED_TYPES = ("RRS", "CALL")
SPURIOUS_MARKERS = ("citado, no en golden",)


def _read_detail(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _is_expected_row(row: dict) -> bool:
    t = row.get("tipo") or ""
    return t in EXPECTED_TYPES


def _is_spurious_row(row: dict) -> bool:
    t = row.get("tipo") or ""
    return any(m in t for m in SPURIOUS_MARKERS)


def _source_from_chunk(chunk_id: str) -> str:
    if not chunk_id:
        return ""
    if "Call-Book" in chunk_id or "Call Book" in chunk_id:
        return "Call Book"
    if "Case-Book" in chunk_id or "Case Book" in chunk_id:
        return "Case Book"
    if chunk_id.startswith("The-Call"):
        return "Call Book"
    if chunk_id.startswith("WS-Case"):
        return "Case Book"
    return "Otro"


def aggregate_detail(rows: list[dict], label: str) -> tuple[list[dict], list[dict], dict]:
    """Devuelve filas agg por tipo, por caso, y dict de métricas globales."""
    agg_tipo: list[dict] = []
    by_case: dict[str, list[dict]] = {}

    for row in rows:
        cid = str(row.get("case_id", ""))
        by_case.setdefault(cid, []).append(row)

    for tipo in EXPECTED_TYPES:
        sub = [r for r in rows if r.get("tipo") == tipo]
        n = len(sub)
        if n == 0:
            continue
        ctx = sum(1 for r in sub if r.get("en_contexto_recuperado") == "si")
        cit = sum(1 for r in sub if r.get("citado_en_respuesta") == "si")
        pipe = sum(
            1
            for r in sub
            if r.get("en_contexto_recuperado") == "si"
            and r.get("citado_en_respuesta") == "si"
        )
        ranks = [
            float(r["rank_primer_chunk"])
            for r in sub
            if r.get("en_contexto_recuperado") == "si" and r.get("rank_primer_chunk")
        ]
        mrr = sum(1.0 / rk for rk in ranks) / n if ranks else 0.0
        call_hits = [
            r for r in sub if r.get("en_contexto_recuperado") == "si" and r.get("chunk_id")
        ]
        from_call = sum(1 for r in call_hits if _source_from_chunk(r["chunk_id"]) == "Call Book")

        agg_tipo.append(
            {
                "corrida": label,
                "tipo": tipo,
                "n_esperados": n,
                "n_en_contexto": ctx,
                "tasa_contexto": ctx / n,
                "n_citados": cit,
                "tasa_cita": cit / n,
                "n_pipeline_ok": pipe,
                "tasa_pipeline": pipe / n,
                "brecha_contexto_cita": (ctx - cit) / n,
                "mrr": mrr,
                "pct_hits_top1": sum(1 for rk in ranks if rk == 1) / len(ranks) if ranks else 0,
                "pct_hits_top3": sum(1 for rk in ranks if rk <= 3) / len(ranks) if ranks else 0,
                "pct_hits_call_book": from_call / len(call_hits) if call_hits else 0,
            }
        )

    spurious = [r for r in rows if _is_spurious_row(r)]
    n_spur_rrs = sum(1 for r in spurious if "RRS" in (r.get("tipo") or ""))
    n_spur_call = sum(1 for r in spurious if "CALL" in (r.get("tipo") or ""))

    per_case_rows: list[dict] = []
    for cid in sorted(by_case.keys(), key=lambda x: int(x) if x.isdigit() else x):
        case_rows = by_case[cid]
        titulo = case_rows[0].get("titulo", "") if case_rows else ""
        rec: dict = {"corrida": label, "case_id": cid, "titulo": titulo}
        for tipo in EXPECTED_TYPES:
            sub = [r for r in case_rows if r.get("tipo") == tipo]
            n = len(sub)
            ctx = sum(1 for r in sub if r.get("en_contexto_recuperado") == "si")
            cit = sum(1 for r in sub if r.get("citado_en_respuesta") == "si")
            rec[f"{tipo.lower()}_esperados"] = n
            rec[f"{tipo.lower()}_en_contexto"] = f"{ctx}/{n}" if n else "0/0"
            rec[f"{tipo.lower()}_citados"] = f"{cit}/{n}" if n else "0/0"
            rec[f"{tipo.lower()}_tasa_contexto"] = ctx / n if n else None
            rec[f"{tipo.lower()}_tasa_cita"] = cit / n if n else None
        per_case_rows.append(rec)

    global_extra = {
        "corrida": label,
        "n_citas_espurias_rrs": n_spur_rrs,
        "n_citas_espurias_call": n_spur_call,
        "n_citas_espurias_total": len(spurious),
    }

    return agg_tipo, per_case_rows, global_extra


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def _plot_tasas_agregadas(agg: list[dict], out: Path, label: str) -> None:
    tipos = [a["tipo"] for a in agg]
    x = np.arange(len(tipos))
    w = 0.25
    ctx = [a["tasa_contexto"] for a in agg]
    cit = [a["tasa_cita"] for a in agg]
    pipe = [a["tasa_pipeline"] for a in agg]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(x - w, ctx, w, label="En contexto (recuperado)", color="#3498db")
    ax.bar(x, cit, w, label="Citado en respuesta", color="#2ecc71")
    ax.bar(x + w, pipe, w, label="Contexto + cita OK", color="#9b59b6")
    ax.set_xticks(x)
    ax.set_xticklabels(tipos)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Tasa (sobre ítems esperados del golden set)")
    ax.set_title(f"Tasas por tipo normativo — {label}")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)


def _plot_por_caso(per_case: list[dict], out: Path, label: str) -> None:
    ids = [r["case_id"] for r in per_case]
    x = np.arange(len(ids))
    w = 0.2

    def series(key: str) -> list[float]:
        return [float(r[key]) if r.get(key) is not None else 0 for r in per_case]

    fig, ax = plt.subplots(figsize=(12, 4.5))
    ax.bar(x - 1.5 * w, series("rrs_tasa_contexto"), w, label="RRS contexto", color="#85c1e9")
    ax.bar(x - 0.5 * w, series("rrs_tasa_cita"), w, label="RRS cita", color="#2874a6")
    ax.bar(x + 0.5 * w, series("call_tasa_contexto"), w, label="CALL contexto", color="#f9e79f")
    ax.bar(x + 1.5 * w, series("call_tasa_cita"), w, label="CALL cita", color="#d4ac0d")
    ax.set_xticks(x)
    ax.set_xticklabels(ids)
    ax.set_xlabel("Caso (ID)")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Tasa")
    ax.set_title(f"Métricas por caso — {label}")
    ax.legend(ncol=2, fontsize=7, loc="upper right")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)


def _collect_hit_ranks(rows: list[dict], tipo: str | None = None) -> list[int]:
    return [
        int(float(r["rank_primer_chunk"]))
        for r in rows
        if (tipo is None or r.get("tipo") == tipo)
        and r.get("en_contexto_recuperado") == "si"
        and r.get("rank_primer_chunk")
    ]


def _count_rank_distribution(
    rows: list[dict],
) -> tuple[list[str], list[int], list[str], int]:
    """Cuenta hits con contexto por rank (1–8), con desglose RRS/CALL en etiquetas."""
    counts = {k: 0 for k in range(1, 9)}
    by_tipo: dict[int, dict[str, int]] = {k: {"RRS": 0, "CALL": 0} for k in range(1, 9)}
    for r in rows:
        if r.get("en_contexto_recuperado") != "si" or not r.get("rank_primer_chunk"):
            continue
        if r.get("tipo") not in ("RRS", "CALL"):
            continue
        k = int(float(r["rank_primer_chunk"]))
        counts[k] += 1
        by_tipo[k][r["tipo"]] += 1

    palette = [
        "#27ae60",
        "#2ecc71",
        "#58d68d",
        "#f4d03f",
        "#f39c12",
        "#e67e22",
        "#e74c3c",
        "#922b21",
    ]
    labels: list[str] = []
    vals: list[int] = []
    colors: list[str] = []
    for k in range(1, 9):
        if counts[k] == 0:
            continue
        parts: list[str] = []
        if by_tipo[k]["RRS"]:
            parts.append(f"{by_tipo[k]['RRS']} RRS")
        if by_tipo[k]["CALL"]:
            parts.append(f"{by_tipo[k]['CALL']} CALL")
        labels.append(f"Rank {k}\n({', '.join(parts)})")
        vals.append(counts[k])
        colors.append(palette[k - 1])
    return labels, vals, colors, sum(vals)


def _plot_rank_distribution(rows: list[dict], out: Path, label: str) -> None:
    fig, ax = plt.subplots(figsize=(8, 4))
    for tipo, color in (("RRS", "#e74c3c"), ("CALL", "#2980b9")):
        ranks = _collect_hit_ranks(rows, tipo=tipo)
        if ranks:
            ax.hist(
                ranks,
                bins=np.arange(0.5, 9.6, 1),
                alpha=0.65,
                label=f"{tipo} (n={len(ranks)})",
                color=color,
                edgecolor="white",
            )
    ax.set_xticks(range(1, 9))
    ax.set_xlabel("Rank del primer chunk con hit")
    ax.set_ylabel("Cantidad de ítems esperados")
    ax.set_title(f"Distribución de ranking — {label}")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)


def _plot_rank_distribution_pie(rows: list[dict], out: Path, label: str) -> None:
    """Torta: % de ítems con hit por rank del primer chunk (top_k=8)."""
    labels, vals, colors, total = _count_rank_distribution(rows)
    if total == 0:
        return

    def autopct(pct: float) -> str:
        n = round(pct * total / 100.0)
        return f"{pct:.1f}%\n(n={n})"

    fig, ax = plt.subplots(figsize=(9, 6))
    _, _, autotexts = ax.pie(
        vals,
        labels=labels,
        colors=colors,
        autopct=autopct,
        startangle=90,
        counterclock=False,
        pctdistance=0.72,
        labeldistance=1.1,
        wedgeprops={"edgecolor": "white", "linewidth": 1.2},
        textprops={"fontsize": 8},
    )
    for t in autotexts:
        t.set_fontsize(9)
        t.set_fontweight("bold")
    ax.set_title(
        f"Distribución de ranking (% con contexto recuperado, n={total}) — {label}",
        pad=16,
        fontsize=11,
    )
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)


def _count_matriz_contexto_cita(rows: list[dict]) -> tuple[dict[str, int], list[str], list[int], list[str]]:
    cells = {"A": 0, "B": 0, "C": 0, "D": 0}
    for r in rows:
        if not _is_expected_row(r):
            continue
        ctx = r.get("en_contexto_recuperado") == "si"
        cit = r.get("citado_en_respuesta") == "si"
        if ctx and cit:
            cells["A"] += 1
        elif ctx and not cit:
            cells["B"] += 1
        elif not ctx and cit:
            cells["C"] += 1
        else:
            cells["D"] += 1

    labels = [
        "A: contexto sí, cita sí",
        "B: contexto sí, cita no",
        "C: contexto no, cita sí",
        "D: contexto no, cita no",
    ]
    vals = [cells["A"], cells["B"], cells["C"], cells["D"]]
    colors = ["#27ae60", "#f39c12", "#9b59b6", "#e74c3c"]
    return cells, labels, vals, colors


def _plot_matriz_contexto_cita(rows: list[dict], out: Path, label: str) -> None:
    """Barras: contexto sí/no × cita sí/no (solo ítems esperados)."""
    cells, labels, vals, colors = _count_matriz_contexto_cita(rows)

    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.bar(
        [
            "A: contexto sí,\ncita sí",
            "B: contexto sí,\ncita no",
            "C: contexto no,\ncita sí",
            "D: contexto no,\ncita no",
        ],
        vals,
        color=colors,
        edgecolor="white",
    )
    ax.set_ylabel("Nº ítems esperados (reglas + CALL)")
    ax.set_title(f"Matriz contexto → cita — {label}")
    for b, v in zip(bars, vals):
        ax.text(
            b.get_x() + b.get_width() / 2,
            v + 0.3,
            str(v),
            ha="center",
            fontsize=10,
        )
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)


def _plot_matriz_contexto_cita_pie(rows: list[dict], out: Path, label: str) -> None:
    """Torta con porcentajes sobre ítems esperados del golden set."""
    cells, labels, vals, colors = _count_matriz_contexto_cita(rows)
    total = sum(vals)
    if total == 0:
        return

    def autopct(pct: float) -> str:
        n = round(pct * total / 100.0)
        return f"{pct:.1f}%\n(n={n})"

    fig, ax = plt.subplots(figsize=(8, 6))
    wedges, texts, autotexts = ax.pie(
        vals,
        labels=labels,
        colors=colors,
        autopct=autopct,
        startangle=90,
        counterclock=False,
        pctdistance=0.75,
        labeldistance=1.08,
        wedgeprops={"edgecolor": "white", "linewidth": 1.2},
        textprops={"fontsize": 9},
    )
    for t in autotexts:
        t.set_fontsize(9)
        t.set_fontweight("bold")
    ax.set_title(
        f"Matriz contexto → cita (% ítems esperados, n={total}) — {label}",
        pad=16,
        fontsize=11,
    )
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)


def _plot_compare_runs(agg_a: list[dict], agg_b: list[dict], label_a: str, label_b: str, out: Path) -> None:
    metrics = [
        ("tasa_contexto", "En contexto"),
        ("tasa_cita", "Citado"),
        ("tasa_pipeline", "Pipeline OK"),
    ]
    tipos = ["RRS", "CALL"]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5), sharey=True)
    for ax, tipo in zip(axes, tipos):
        a = next((x for x in agg_a if x["tipo"] == tipo), None)
        b = next((x for x in agg_b if x["tipo"] == tipo), None)
        if not a or not b:
            continue
        x = np.arange(len(metrics))
        w = 0.35
        for i, (key, lab) in enumerate(metrics):
            va = a[key]
            vb = b[key]
            ax.bar(i - w / 2, va, w, label=label_a if i == 0 else "", color="#95a5a6")
            ax.bar(i + w / 2, vb, w, label=label_b if i == 0 else "", color="#2ecc71")
            ax.text(i - w / 2, va + 0.02, f"{va:.0%}", ha="center", fontsize=7)
            ax.text(i + w / 2, vb + 0.02, f"{vb:.0%}", ha="center", fontsize=7)
        ax.set_xticks(x)
        ax.set_xticklabels([m[1] for m in metrics], fontsize=8)
        ax.set_ylim(0, 1.1)
        ax.set_title(tipo)
        ax.grid(axis="y", alpha=0.25)
    axes[0].set_ylabel("Tasa")
    fig.suptitle("Comparación de corridas", y=1.02, fontsize=11)
    axes[1].legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)


def process_run(run_dir: Path, label: str | None = None) -> Path:
    detail_path = run_dir / "retrieval_hits_detail.csv"
    if not detail_path.is_file():
        raise FileNotFoundError(f"No existe {detail_path}. Ejecutá export_retrieval_hits_csv.py primero.")

    label = label or run_dir.name
    rows = _read_detail(detail_path)
    agg_tipo, per_case, global_extra = aggregate_detail(rows, label)

    for a in agg_tipo:
        a.update(global_extra)

    agg_fields = list(agg_tipo[0].keys()) if agg_tipo else []
    case_fields = list(per_case[0].keys()) if per_case else []

    _write_csv(run_dir / "retrieval_hits_agg.csv", agg_fields, agg_tipo)
    _write_csv(run_dir / "retrieval_hits_por_caso_agg.csv", case_fields, per_case)

    plots_dir = run_dir / "plots_retrieval"
    plots_dir.mkdir(exist_ok=True)
    _plot_tasas_agregadas(agg_tipo, plots_dir / "01_tasas_por_tipo.png", label)
    _plot_por_caso(per_case, plots_dir / "02_tasas_por_caso.png", label)
    _plot_rank_distribution(rows, plots_dir / "03_distribucion_rank.png", label)
    _plot_rank_distribution_pie(rows, plots_dir / "03_distribucion_rank_torta.png", label)
    _plot_matriz_contexto_cita(rows, plots_dir / "04_matriz_contexto_cita.png", label)
    _plot_matriz_contexto_cita_pie(
        rows, plots_dir / "04_matriz_contexto_cita_torta.png", label
    )

    return plots_dir


def main() -> None:
    p = argparse.ArgumentParser(description="Agregar retrieval_hits_detail y graficar")
    p.add_argument(
        "run_dir",
        type=Path,
        nargs="?",
        default=ROOT / "eval" / "corrida baseline",
        help="Carpeta con retrieval_hits_detail.csv",
    )
    p.add_argument("--label", default=None, help="Etiqueta de la corrida en CSV/gráficos")
    p.add_argument(
        "--compare",
        type=Path,
        default=None,
        help="Segunda carpeta de corrida para gráfico comparativo",
    )
    p.add_argument("--label-compare", default=None)
    args = p.parse_args()

    plots = process_run(args.run_dir, args.label)
    print(f"CSV: {args.run_dir / 'retrieval_hits_agg.csv'}")
    print(f"CSV: {args.run_dir / 'retrieval_hits_por_caso_agg.csv'}")
    print(f"Gráficos: {plots}")

    if args.compare:
        label_a = args.label or args.run_dir.name
        label_b = args.label_compare or args.compare.name
        rows_a = _read_detail(args.run_dir / "retrieval_hits_detail.csv")
        rows_b = _read_detail(args.compare / "retrieval_hits_detail.csv")
        agg_a, _, _ = aggregate_detail(rows_a, label_a)
        agg_b, _, _ = aggregate_detail(rows_b, label_b)
        out_cmp = args.run_dir / "plots_retrieval" / "05_comparacion_corridas.png"
        if args.compare != args.run_dir:
            _plot_compare_runs(agg_a, agg_b, label_a, label_b, out_cmp)
            print(f"Comparación: {out_cmp}")


if __name__ == "__main__":
    main()
