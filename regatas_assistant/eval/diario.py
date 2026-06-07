"""Actualización automática de eval/DIARIO_PRUEBAS.md tras cada corrida."""

from __future__ import annotations

import csv
import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
EVAL_DIR = ROOT / "eval"
BASELINE_DIR = EVAL_DIR / "corrida baseline"
RUNS_DIR = EVAL_DIR / "runs"
DIARIO_MD = EVAL_DIR / "DIARIO_PRUEBAS.md"
REGISTRY_JSON = EVAL_DIR / "diario_runs.json"

# Run ID oficial de la línea base (carpeta corrida baseline)
BASELINE_RUN_ID = "20260525_185138_baseline_call_case_qwen_es"

METRIC_KEYS = [
    ("mean_recall_at_k_rules", "Recall@k reglas"),
    ("mean_recall_at_k_calls", "Recall@k CALL"),
    ("mean_citation_f1_rrs", "F1 citas RRS"),
    ("mean_citation_f1_calls", "F1 citas CALL"),
    ("mean_token_jaccard_answer_context", "Jaccard resp↔ctx"),
    ("mean_token_jaccard_answer_reference", "Jaccard resp↔ref"),
    ("verdict_accuracy", "Dictamen auto"),
    ("mean_faithfulness_rate", "Faithfulness"),
    ("mean_faithfulness_rate_strict", "Faithfulness estricta"),
]


@dataclass
class RunEntry:
    exp_id: str
    run_id: str
    label: str
    created_at: str
    run_dir: str
    index_summary: str = ""
    retrieval_only: bool = False
    settings: dict[str, Any] = field(default_factory=dict)
    aggregate: dict[str, Any] = field(default_factory=dict)
    retrieval: dict[str, Any] = field(default_factory=dict)
    matriz: dict[str, int] = field(default_factory=dict)
    cambios_vs_anterior: list[str] = field(default_factory=list)
    comparativa_vs_baseline: list[str] = field(default_factory=list)
    comparativa_vs_anterior: list[str] = field(default_factory=list)
    nota_usuario: str = ""
    is_baseline: bool = False


def _load_report(run_dir: Path) -> dict[str, Any] | None:
    p = run_dir / "report.json"
    if not p.is_file():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def _index_summary(settings: dict[str, Any]) -> str:
    sources = settings.get("corpus_sources") or "pdf"
    files = settings.get("corpus_filenames") or []
    proc = settings.get("load_processed_jsonl")
    parts: list[str] = []
    if proc and sources in ("processed", "full", None):
        parts.append("RRS JSONL+def (~495 ch.)")
    if sources in ("pdf", "full", None) and files:
        n = "Call+Case PDF (~894 ch.)" if len(files) >= 2 else ", ".join(files)
        parts.append(n)
    elif sources == "processed":
        parts.append("solo processed")
    if sources == "full" and proc and files:
        return " + ".join(parts) + " ≈1389 ch."
    return ", ".join(parts) if parts else "—"


def _fmt_pct(x: float | None) -> str:
    if x is None:
        return "—"
    return f"{x * 100:.1f} %"


def _fmt_num(x: float | None) -> str:
    if x is None:
        return "—"
    return f"{x:.2f}"


def _read_retrieval_agg(run_dir: Path) -> dict[str, Any]:
    p = run_dir / "retrieval_hits_agg.csv"
    out: dict[str, Any] = {}
    if not p.is_file():
        return out
    for row in csv.DictReader(p.open(encoding="utf-8-sig")):
        tipo = row.get("tipo", "")
        out[tipo] = {
            "tasa_contexto": float(row.get("tasa_contexto") or 0),
            "tasa_pipeline": float(row.get("tasa_pipeline") or 0),
            "n_en_contexto": row.get("n_en_contexto"),
            "n_esperados": row.get("n_esperados"),
        }
    return out


def _read_matriz(run_dir: Path) -> dict[str, int]:
    p = run_dir / "retrieval_hits_detail.csv"
    cells = {"A": 0, "B": 0, "C": 0, "D": 0}
    rrs_hits = 0
    if not p.is_file():
        return cells
    for row in csv.DictReader(p.open(encoding="utf-8-sig")):
        if row.get("tipo") not in ("RRS", "CALL"):
            continue
        ctx = row.get("en_contexto_recuperado") == "si"
        cit = row.get("citado_en_respuesta") == "si"
        key = "A" if ctx and cit else "B" if ctx else "C" if cit else "D"
        cells[key] += 1
        if ctx and (row.get("chunk_id") or "").startswith("rrs|"):
            rrs_hits += 1
    cells["rrs_hits"] = rrs_hits
    return cells


def _settings_diff(prev: dict, curr: dict) -> list[str]:
    lines: list[str] = []
    keys = [
        ("corpus_sources", "Fuentes corpus"),
        ("corpus_filenames", "PDFs"),
        ("load_processed_jsonl", "JSONL processed"),
        ("chunk_size", "chunk_size"),
        ("chunk_overlap", "chunk_overlap"),
        ("retrieve_top_k", "top_k"),
        ("retrieval_use_quotas", "cupos retrieval"),
        ("retrieval_quota_by_doctype", "cupos por tipo"),
        ("retrieval_quota_rrs", "cupo rrs"),
        ("retrieval_quota_call", "cupo call"),
        ("retrieval_quota_case", "cupo case"),
        ("retrieval_quota_definition", "cupo def"),
        ("retrieval_quota_processed", "cupo processed"),
        ("retrieval_quota_pdf", "cupo PDF"),
        ("embedding_backend", "embedding"),
        ("llm_model", "modelo LLM"),
        ("system_prompt_language", "idioma prompt"),
        ("response_language", "idioma respuesta"),
        ("prompt_strategy", "estrategia prompt"),
    ]
    for key, label in keys:
        a, b = prev.get(key), curr.get(key)
        if a != b:
            lines.append(f"**{label}:** `{a}` → `{b}`")
    return lines


def _metric_delta_line(name: str, base: float | None, cur: float | None) -> str | None:
    if base is None and cur is None:
        return None
    if base is None:
        return f"- {name}: — → {_fmt_num(cur)}"
    if cur is None:
        return f"- {name}: {_fmt_num(base)} → —"
    d = cur - base
    sign = "+" if d >= 0 else ""
    return f"- {name}: {_fmt_num(base)} → {_fmt_num(cur)} ({sign}{d:.2f})"


def _compare_metrics(
    ref: dict[str, Any], cur: dict[str, Any], titulo: str
) -> list[str]:
    lines = [f"**{titulo}**"]
    for key, label in METRIC_KEYS:
        line = _metric_delta_line(label, ref.get(key), cur.get(key))
        if line:
            lines.append(line)
    return lines


def _infer_cambios(prev: RunEntry | None, cur: RunEntry) -> list[str]:
    if prev is None:
        return ["Primera corrida registrada en el diario (sin anterior)."]
    auto = _settings_diff(prev.settings, cur.settings)
    if not auto:
        return ["Misma configuración de corpus/retriever/LLM que la corrida anterior; variación solo en resultados estocásticos o artefactos."]
    return auto


def _infer_hallazgo(entry: RunEntry, baseline: RunEntry | None) -> str:
    a = entry.aggregate
    if entry.retrieval_only:
        return "Solo retrieval: validación de métricas sin generación LLM."
    if baseline and entry.exp_id != baseline.exp_id:
        dr = (a.get("mean_recall_at_k_rules") or 0) - (
            baseline.aggregate.get("mean_recall_at_k_rules") or 0
        )
        if dr < -0.05:
            return "Recall de reglas por debajo del baseline; revisar ranking o cupos por fuente."
        if dr > 0.05:
            return "Mejora de recall de reglas respecto al baseline."
    rrs = entry.retrieval.get("RRS", {})
    if rrs.get("tasa_contexto", 0) >= 0.35:
        return "Recuperación RRS en contexto aceptable para esta configuración."
    return "Ver comparativas abajo; revisar `retrieval_hits_detail.csv` y gráficos en `plots_retrieval/`."


def _infer_missing_settings(report: dict[str, Any], settings: dict[str, Any]) -> dict[str, Any]:
    """Completa settings en reportes viejos sin corpus_sources."""
    s = dict(settings)
    label = (report.get("label") or "").lower()
    if s.get("corpus_sources"):
        return s
    if label == "rrs_only" or "rrs_only" in label:
        s["corpus_sources"] = "processed"
        s["load_processed_jsonl"] = True
        s["corpus_filenames"] = []
    elif "ingesta_rrs" in label or "rrs_jsonl" in label:
        s["corpus_sources"] = "full"
        s["load_processed_jsonl"] = True
    elif "rrs_case" in label or "rrs_pdf" in label:
        s["corpus_sources"] = "pdf"
        s.setdefault(
            "corpus_filenames",
            [
                "2025-2028-RRS-with-Changes-and-Corrections.pdf",
                "WS-Case-Book-2025-2028-v2025-07.pdf",
            ],
        )
    else:
        s.setdefault("corpus_sources", "pdf")
    return s


def _exp_sort_key(e: RunEntry) -> tuple[int, int]:
    if e.exp_id == "E0":
        return (0, 0)
    m = re.match(r"E(\d+)", e.exp_id or "")
    return (1, int(m.group(1)) if m else 999)


def entry_from_report(run_dir: Path, report: dict[str, Any]) -> RunEntry:
    settings = _infer_missing_settings(report, report.get("settings") or {})
    agg = report.get("aggregate") or {}
    run_id = report.get("run_id", run_dir.name)
    rel = _read_retrieval_agg(run_dir)
    mat = _read_matriz(run_dir)
    return RunEntry(
        exp_id="",
        run_id=run_id,
        label=report.get("label", run_dir.name),
        created_at=report.get("created_at", ""),
        run_dir=str(run_dir.relative_to(ROOT)),
        index_summary=_index_summary(settings),
        retrieval_only=bool(report.get("retrieval_only")),
        settings=settings,
        aggregate=agg,
        retrieval=rel,
        matriz=mat,
        is_baseline=run_id == BASELINE_RUN_ID
        or "corrida baseline" in str(run_dir),
    )


def discover_all_runs() -> list[RunEntry]:
    entries: list[RunEntry] = []
    if BASELINE_DIR.is_dir():
        rep = _load_report(BASELINE_DIR)
        if rep:
            entries.append(entry_from_report(BASELINE_DIR, rep))
    if RUNS_DIR.is_dir():
        for d in sorted(RUNS_DIR.iterdir()):
            if not d.is_dir():
                continue
            rep = _load_report(d)
            if rep:
                entries.append(entry_from_report(d, rep))
    entries.sort(key=_exp_sort_key)
    return entries


def _load_registry() -> dict[str, Any]:
    if REGISTRY_JSON.is_file():
        return json.loads(REGISTRY_JSON.read_text(encoding="utf-8"))
    return {"runs": {}, "next_index": 0}


def _save_registry(data: dict[str, Any]) -> None:
    REGISTRY_JSON.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _assign_exp_ids(entries: list[RunEntry], registry: dict[str, Any]) -> None:
    runs_map: dict[str, str] = registry.get("runs") or {}
    # E0 fijo para baseline
    for e in entries:
        if e.is_baseline or e.run_id == BASELINE_RUN_ID:
            e.exp_id = "E0"
            runs_map[e.run_id] = "E0"

    n = int(registry.get("next_index") or 0)
    if n < 1:
        n = 1
    for e in entries:
        if e.exp_id:
            continue
        if e.run_id in runs_map:
            e.exp_id = runs_map[e.run_id]
            continue
        e.exp_id = f"E{n}"
        runs_map[e.run_id] = e.exp_id
        n += 1
    registry["runs"] = runs_map
    registry["next_index"] = n


def enrich_entries(entries: list[RunEntry]) -> None:
    baseline = next((e for e in entries if e.exp_id == "E0"), None)
    chrono = sorted(entries, key=lambda e: e.created_at or e.run_id)
    chrono_idx = {e.run_id: i for i, e in enumerate(chrono)}
    for e in entries:
        i = chrono_idx.get(e.run_id, 0)
        prev = chrono[i - 1] if i > 0 else None
        if prev and prev.run_id == e.run_id:
            prev = chrono[i - 2] if i > 1 else None
        e.cambios_vs_anterior = _infer_cambios(prev, e)
        if baseline and e.exp_id != "E0":
            e.comparativa_vs_baseline = _compare_metrics(
                baseline.aggregate, e.aggregate, "vs E0 (baseline)"
            )
        if prev:
            e.comparativa_vs_anterior = _compare_metrics(
                prev.aggregate, e.aggregate, f"vs {prev.exp_id} (`{prev.label}`)"
            )


def _rel_link(run_dir: str) -> str:
    if "corrida baseline" in run_dir:
        return f"[`{run_dir}`]({run_dir.replace(' ', '%20')}/)"
    name = Path(run_dir).name
    return f"[`eval/runs/{name}/`](runs/{name}/)"


def render_diario(entries: list[RunEntry]) -> str:
    lines: list[str] = [
        "# Diario de pruebas — evaluación RAG (asistente de protestas)",
        "",
        "Documento **generado automáticamente** al finalizar cada `eval_run.py`. "
        "No editar a mano las secciones §1–§4; usar `eval/diario_runs.json` (`nota_usuario`) "
        "o `--diario-nota` si hace falta aclarar algo.",
        "",
        f"**Última regeneración:** {datetime.now().strftime('%Y-%m-%d %H:%M')} (local)",
        "",
        "**Golden set fijo (15 casos):** `docs/Casos de Regatas.xlsx` → `eval/data/eval_set.json`.",
        "",
        "**Línea base oficial:** **E0** — `eval/corrida baseline/`, tag git `v0.1.0-baseline`.",
        "",
        "---",
        "",
        "## 1. Tabla maestra de corridas",
        "",
        "| ID | Fecha (UTC) | Etiqueta | Run ID | Índice RAG | LLM | Modo | R@k reglas | R@k CALL | F1 RRS | F1 CALL | Carpeta |",
        "|----|-------------|----------|--------|------------|-----|------|------------|----------|--------|---------|---------|",
    ]
    for e in entries:
        modo = "solo retrieval" if e.retrieval_only else "completo"
        model = e.settings.get("llm_model") or "—"
        rid = e.run_id[:20] + "…" if len(e.run_id) > 22 else e.run_id
        mark = "**" if e.exp_id == "E0" else ""
        lines.append(
            f"| {mark}{e.exp_id}{mark} | {e.created_at[:10]} | `{e.label}` | `{rid}` | "
            f"{e.index_summary} | {model} | {modo} | "
            f"{_fmt_num(e.aggregate.get('mean_recall_at_k_rules'))} | "
            f"{_fmt_num(e.aggregate.get('mean_recall_at_k_calls'))} | "
            f"{_fmt_num(e.aggregate.get('mean_citation_f1_rrs'))} | "
            f"{_fmt_num(e.aggregate.get('mean_citation_f1_calls'))} | "
            f"{_rel_link(e.run_dir)} |"
        )
    lines.extend(
        [
            "",
            "---",
            "",
            "## 2. Métricas de retrieval (golden set)",
            "",
            "| ID | RRS contexto | RRS pipeline | CALL contexto | CALL pipeline | Hits `rrs\\|` | A | B | C | D |",
            "|----|--------------|--------------|---------------|---------------|-------------|---|---|---|---|",
        ]
    )
    for e in entries:
        rrs = e.retrieval.get("RRS", {})
        call = e.retrieval.get("CALL", {})
        m = e.matriz
        lines.append(
            f"| {e.exp_id} | {_fmt_pct(rrs.get('tasa_contexto'))} | "
            f"{_fmt_pct(rrs.get('tasa_pipeline'))} | "
            f"{_fmt_pct(call.get('tasa_contexto'))} | "
            f"{_fmt_pct(call.get('tasa_pipeline'))} | "
            f"{m.get('rrs_hits', '—')} | {m.get('A', '—')} | {m.get('B', '—')} | "
            f"{m.get('C', '—')} | {m.get('D', '—')} |"
        )
    lines.extend(["", "---", "", "## 3. Detalle por corrida (auto + comparativas)", ""])
    for e in entries:
        lines.append(f"### {e.exp_id} — `{e.label}`")
        lines.append("")
        lines.append(f"**Run ID:** `{e.run_id}`  ")
        lines.append(f"**Carpeta:** `{e.run_dir}`  ")
        if e.nota_usuario:
            lines.append(f"**Nota:** {e.nota_usuario}  ")
        lines.append("")
        lines.append("#### Qué cambió respecto a la corrida anterior")
        lines.append("")
        for c in e.cambios_vs_anterior:
            lines.append(f"- {c}")
        lines.append("")
        if e.comparativa_vs_anterior and (
            not e.comparativa_vs_baseline
            or e.comparativa_vs_anterior != e.comparativa_vs_baseline
        ):
            lines.append("#### Comparativa vs corrida anterior")
            lines.append("")
            lines.extend(e.comparativa_vs_anterior[1:] or e.comparativa_vs_anterior)
            lines.append("")
        if e.comparativa_vs_baseline and e.exp_id != "E0":
            lines.append("#### Comparativa vs E0 (baseline)")
            lines.append("")
            lines.extend(e.comparativa_vs_baseline[1:])
            lines.append("")
        lines.append("#### Configuración")
        lines.append("")
        lines.append(f"- Índice: {e.index_summary}")
        lines.append(f"- `corpus_sources`: `{e.settings.get('corpus_sources', 'pdf')}`")
        lines.append(f"- Retrieval: `{e.settings.get('embedding_backend')}`, top_k={e.settings.get('retrieve_top_k')}")
        lines.append(f"- Hallazgo (auto): {_infer_hallazgo(e, next((x for x in entries if x.exp_id == 'E0'), None))}")
        lines.append("")
        if (Path(ROOT) / e.run_dir / "plots_retrieval" / "05_comparacion_corridas.png").is_file():
            lines.append("- Gráfico vs baseline: `plots_retrieval/05_comparacion_corridas.png`")
        lines.append("")
        lines.append("---")
        lines.append("")

    lines.extend(
        [
            "## 4. Comparación rápida vs E0 (solo corridas con LLM)",
            "",
            "| ID | Δ recall reglas | Δ recall CALL | Δ F1 RRS | Δ F1 CALL |",
            "|----|-----------------|---------------|----------|-----------|",
        ]
    )
    baseline = next((e for e in entries if e.exp_id == "E0"), None)
    if baseline:
        for e in entries:
            if e.retrieval_only or e.exp_id == "E0":
                continue
            ba, ea = baseline.aggregate, e.aggregate

            def d(k: str) -> str:
                a, b = ba.get(k), ea.get(k)
                if a is None or b is None:
                    return "—"
                return f"{b - a:+.2f}"

            lines.append(
                f"| {e.exp_id} | {d('mean_recall_at_k_rules')} | {d('mean_recall_at_k_calls')} | "
                f"{d('mean_citation_f1_rrs')} | {d('mean_citation_f1_calls')} |"
            )

    lines.extend(
        [
            "",
            "## 5. Registro automático",
            "",
            "Tras cada corrida, `eval_run.py` ejecuta:",
            "",
            "1. `export_retrieval_hits_csv.py` (si hay `retrieval_hits.json`)",
            "2. `aggregate_retrieval_hits.py` con `--compare` al baseline",
            "3. `compare_eval_runs.py` vs `eval/corrida baseline`",
            "4. Regeneración de este archivo",
            "",
            "Comando manual:",
            "",
            "```bash",
            "python scripts/update_diario_pruebas.py eval/runs/<run_id>",
            "# o solo regenerar todo:",
            "python scripts/update_diario_pruebas.py --all",
            "```",
            "",
            "Nota opcional en la corrida:",
            "",
            "```bash",
            "python scripts/eval_run.py --label mi_prueba --diario-nota \"Probamos top_k=16\" ...",
            "```",
            "",
            "## 6. Scripts relacionados",
            "",
            "| Script | Uso |",
            "|--------|-----|",
            "| `scripts/eval_run.py` | Corrida + actualiza diario |",
            "| `scripts/update_diario_pruebas.py` | Solo regenerar diario |",
            "| `scripts/compare_eval_runs.py` | Δ entre dos report.json |",
            "| `scripts/aggregate_retrieval_hits.py` | Gráficos retrieval |",
            "",
            "---",
            "",
            "*Fin del diario autogenerado.*",
            "",
        ]
    )
    return "\n".join(lines)


def update_diario_after_run(
    run_dir: Path,
    *,
    nota: str = "",
    compare_baseline: bool = True,
) -> Path:
    """Registra la corrida, enriquece comparativas y regenera DIARIO_PRUEBAS.md."""
    run_dir = run_dir.resolve()
    report = _load_report(run_dir)
    if not report:
        raise FileNotFoundError(f"No hay report.json en {run_dir}")

    registry = _load_registry()
    if nota:
        registry.setdefault("notes", {})[report["run_id"]] = nota
        _save_registry(registry)

    entries = discover_all_runs()
    _assign_exp_ids(entries, registry)
    _save_registry(registry)

    for e in entries:
        if e.run_id == report["run_id"]:
            notes = registry.get("notes") or {}
            e.nota_usuario = notes.get(e.run_id, "")

    enrich_entries(entries)
    DIARIO_MD.write_text(render_diario(entries), encoding="utf-8")

    # Comparación markdown en carpeta de corrida
    if compare_baseline and BASELINE_DIR.is_dir():
        _write_comparacion_carpeta(run_dir, entries)

    return DIARIO_MD


def _write_comparacion_carpeta(run_dir: Path, entries: list[RunEntry]) -> None:
    run_dir = run_dir.resolve()
    cur = next(
        (e for e in entries if (ROOT / e.run_dir).resolve() == run_dir),
        None,
    )
    if not cur:
        return
    baseline = next((e for e in entries if e.exp_id == "E0"), None)
    prev = None
    for i, e in enumerate(entries):
        if e.run_id == cur.run_id and i > 0:
            prev = entries[i - 1]
            break
    lines = [
        f"# Comparación — `{cur.label}` ({cur.exp_id})",
        "",
        f"**Run ID:** `{cur.run_id}`",
        "",
        "## Qué cambió respecto a la corrida anterior",
        "",
    ]
    lines.extend(f"- {c}" for c in cur.cambios_vs_anterior)
    lines.append("")
    if prev:
        lines.append(f"## Comparativa vs {prev.exp_id} (`{prev.label}`)")
        lines.append("")
        lines.extend(cur.comparativa_vs_anterior[1:] if cur.comparativa_vs_anterior else ["—"])
        lines.append("")
    if baseline and cur.exp_id != "E0":
        lines.append("## Comparativa vs E0 (baseline)")
        lines.append("")
        lines.extend(cur.comparativa_vs_baseline[1:] if cur.comparativa_vs_baseline else ["—"])
        lines.append("")
    out = run_dir / "comparacion_vs_baseline.md"
    if prev and prev.exp_id != "E0":
        also = run_dir / f"comparacion_vs_{prev.exp_id}.md"
        also.write_text("\n".join(lines), encoding="utf-8")
    out.write_text("\n".join(lines), encoding="utf-8")


def regenerate_all() -> Path:
    registry = _load_registry()
    entries = discover_all_runs()
    _assign_exp_ids(entries, registry)
    _save_registry(registry)
    notes = registry.get("notes") or {}
    for e in entries:
        e.nota_usuario = notes.get(e.run_id, "")
    enrich_entries(entries)
    DIARIO_MD.write_text(render_diario(entries), encoding="utf-8")
    return DIARIO_MD
