"""Consola de actividad en ventana aparte (tkinter, proceso independiente).

Al ejecutar ``python app.py`` en local se abre la ventana al arrancar (salvo HF Space
o ``REGATAS_ACTIVITY_CONSOLE=0``). Registra envíos al LLM y notas de carga.
"""

from __future__ import annotations

import os
import queue
import re
import threading
from datetime import datetime, timezone
from multiprocessing import Process, Queue, get_context
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from regatas_assistant.ingestion import TextChunk

_CLEAR_SENTINEL = "__REGATAS_CLEAR__"
_RULE_REF_RE = re.compile(
    r"(?i)\b(?:rule|r\.)\s*(\d{1,2}(?:\.\d+)*)\b|\bcall\s+(\d{1,4})\b|\bcase\s+(\d{1,4})\b"
)

_lines: list[str] = []
_lines_lock = threading.Lock()
_enabled: bool | None = None
_mp_queue: Queue[str] | None = None
_gui_process: Process | None = None
_start_lock = threading.Lock()


def _env_disabled() -> bool:
    v = os.environ.get("REGATAS_ACTIVITY_CONSOLE", "").strip().lower()
    return v in ("0", "false", "no", "off")


def is_enabled() -> bool:
    global _enabled
    if _enabled is None:
        _enabled = not _env_disabled()
    return _enabled


def set_enabled(value: bool) -> None:
    global _enabled
    _enabled = value


def should_open_on_launch(*, in_space: bool = False) -> bool:
    if in_space:
        return False
    return is_enabled()


def _append_line(line: str) -> None:
    with _lines_lock:
        _lines.append(line)
    q = _mp_queue
    if q is not None:
        try:
            q.put_nowait(line)
        except Exception:
            pass


def get_log_text() -> str:
    with _lines_lock:
        if not _lines:
            return ""
        return "\n".join(_lines)


def clear_log() -> None:
    with _lines_lock:
        _lines.clear()
    q = _mp_queue
    if q is not None:
        try:
            q.put_nowait(_CLEAR_SENTINEL)
        except Exception:
            pass


def clear_for_new_query() -> None:
    """Vacía la consola al iniciar cada consulta del usuario."""
    if not is_enabled():
        return
    clear_log()


def log_model_request(
    *,
    backend: str,
    model: str | None = None,
    user_chars: int | None = None,
) -> None:
    if not is_enabled():
        return
    ts = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S")
    parts = [f"[{ts}] Consulta al modelo enviada", f"backend={backend}"]
    if model:
        parts.append(f"modelo={model}")
    if user_chars is not None:
        parts.append(f"prompt_usuario={user_chars:,} caracteres")
    _append_line(" · ".join(parts))


def log_note(message: str) -> None:
    if not is_enabled():
        return
    ts = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S")
    _append_line(f"[{ts}] {message}")


def _extract_rule_refs(text: str) -> list[str]:
    refs: list[str] = []
    for m in _RULE_REF_RE.finditer(text):
        g = next((x for x in m.groups() if x), None)
        if not g:
            continue
        if m.group(0).lower().startswith("call"):
            refs.append(f"Call {g}")
        elif m.group(0).lower().startswith("case"):
            refs.append(f"Case {g}")
        else:
            refs.append(f"Rule {g}")
    return refs


def _sort_ref_key(label: str) -> tuple:
    m = re.search(r"(\d+(?:\.\d+)*)", label)
    if not m:
        return (99, label)
    parts = [int(x) for x in m.group(1).split(".")]
    return (0, parts)


def log_retrieved_context(chunks: list[TextChunk]) -> None:
    """Tras la respuesta del LLM, lista fragmentos recuperados y referencias detectadas."""
    if not is_enabled():
        return
    if not chunks:
        log_note("Sin fragmentos recuperados del corpus para esta consulta.")
        return
    log_note(f"Reglas y contexto recuperados ({len(chunks)} fragmento(s)):")
    all_refs: list[str] = []
    for i, chunk in enumerate(chunks, 1):
        preview = re.sub(r"\s+", " ", chunk.text).strip()
        if len(preview) > 140:
            preview = preview[:140] + "…"
        log_note(f"  {i}. {chunk.header_line()}")
        if preview:
            log_note(f"     {preview}")
        all_refs.extend(_extract_rule_refs(chunk.text))
    if all_refs:
        unique = sorted(set(all_refs), key=_sort_ref_key)
        log_note("Referencias citables detectadas: " + ", ".join(unique))


def _console_font(root) -> tuple[str, int]:
    """Tupla (familia, tamaño) válida para tkinter; requiere root ya creado."""
    import tkinter.font as tkfont

    for family in ("Menlo", "Monaco", "Consolas", "Courier New", "Courier"):
        try:
            if family in tkfont.families(root=root):
                return (family, 11)
        except tk.TclError:
            continue
    return ("Courier", 11)


def _tk_main(msg_queue: Queue[str]) -> None:
    import tkinter as tk
    from tkinter import scrolledtext

    root = tk.Tk()
    console_font = _console_font(root)
    root.title("Regatas — Consola de actividad")
    root.geometry("760x340")
    root.minsize(520, 220)
    try:
        root.lift()
        root.attributes("-topmost", True)
        root.after(600, lambda: root.attributes("-topmost", False))
    except tk.TclError:
        pass

    frame = tk.Frame(root, bg="#1e1e1e")
    frame.pack(fill=tk.BOTH, expand=True)

    text = scrolledtext.ScrolledText(
        frame,
        wrap=tk.WORD,
        font=console_font,
        bg="#1e1e1e",
        fg="#d4d4d4",
        insertbackground="#d4d4d4",
        state=tk.DISABLED,
        borderwidth=0,
        highlightthickness=0,
    )
    text.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

    def append_line(line: str) -> None:
        text.configure(state=tk.NORMAL)
        text.insert(tk.END, line + "\n")
        text.see(tk.END)
        text.configure(state=tk.DISABLED)

    append_line(
        "Consola de actividad (ventana independiente). "
        "Se limpia en cada consulta; tras la respuesta del LLM se listan los fragmentos recuperados.\n"
        + ("—" * 52)
    )

    def pump_queue() -> None:
        try:
            while True:
                line = msg_queue.get_nowait()
                if line == _CLEAR_SENTINEL:
                    text.configure(state=tk.NORMAL)
                    text.delete("1.0", tk.END)
                    text.configure(state=tk.DISABLED)
                    continue
                append_line(line)
        except queue.Empty:
            pass
        root.after(120, pump_queue)

    def on_close() -> None:
        root.iconify()

    root.protocol("WM_DELETE_WINDOW", on_close)
    pump_queue()
    root.mainloop()


def start_window(*, allow_gui: bool = True) -> bool:
    """Abre la ventana en un proceso aparte (recomendado en macOS)."""
    global _mp_queue, _gui_process
    if not allow_gui:
        return False
    with _start_lock:
        if _gui_process is not None and _gui_process.is_alive():
            return True
        try:
            import tkinter  # noqa: F401
        except ImportError:
            return False
        ctx = get_context("spawn")
        _mp_queue = ctx.Queue()
        _gui_process = ctx.Process(
            target=_tk_main,
            args=(_mp_queue,),
            name="regatas-activity-console",
            daemon=True,
        )
        _gui_process.start()
        return True


def launch_on_startup(*, in_space: bool = False) -> bool:
    """Activa el registro y abre la ventana al iniciar la app local."""
    if not should_open_on_launch(in_space=in_space):
        set_enabled(False)
        return False
    set_enabled(True)
    if not start_window(allow_gui=True):
        log_note(
            "No se pudo abrir la ventana (tkinter no disponible). "
            "Los mensajes no se mostrarán."
        )
        return False
    log_note("Consola iniciada con la aplicación.")
    return True
