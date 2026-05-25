"""
Interfaz Gradio del asistente de protestas.
Ejecución local: Ollama con Llama 3 (`ollama pull llama3`) y `python app.py` (API compatible en 127.0.0.1:11434).
Hugging Face Space: por defecto `REGATAS_LLM_BACKEND=stub` salvo que configures API remota y secretos.
"""

from __future__ import annotations

import os
import sys
import threading
from collections.abc import Iterator
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import gradio as gr

from regatas_assistant import __version__
from regatas_assistant.activity_console import clear_for_new_query
from regatas_assistant.activity_console import is_enabled as activity_console_enabled
from regatas_assistant.activity_console import launch_on_startup
from regatas_assistant.activity_console import log_note
from regatas_assistant.config import Settings, is_huggingface_space
from regatas_assistant.ollama_models import (
    default_choice as ollama_default_choice,
    list_installed_ollama_models,
)
from regatas_assistant.pipeline import ProtestPipeline

_pipeline: ProtestPipeline | None = None
_pipeline_lock = threading.Lock()

_ANALYSIS_PENDING_HTML = (
    '<p class="analysis-pending-line">'
    '<span class="analysis-pending-spinner" aria-hidden="true"></span>'
    " Generando el informe..."
    "</p>"
)

# Banner panorámico del encabezado (repo / Space)
_HERO_IMAGE = ROOT / "navegacion-vela-regata-2.jpg"

# Fondo celeste claro; los cuadros de relato se fuerzan a blanco vía .relato-input
_PAGE_CSS = """
:root, body, .gradio-container {
    --body-background-fill: #d8eef9 !important;
    --background-fill-primary: #d8eef9 !important;
}
body {
    background-color: #d8eef9 !important;
}
.gradio-container {
    background-color: #d8eef9 !important;
}
main.gradio-main {
    background-color: #d8eef9 !important;
}
.app-header {
    max-width: 72rem;
    margin-left: auto;
    margin-right: auto;
    margin-bottom: 0.35rem;
}
.app-hero-banner {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 6px 28px rgba(15, 45, 75, 0.14);
    margin-bottom: 0.65rem !important;
}
.app-hero-banner img {
    width: 100% !important;
    max-height: 200px !important;
    min-height: 140px !important;
    height: auto !important;
    object-fit: cover !important;
    object-position: 18% center !important;
    display: block !important;
}
.app-title-wrap {
    text-align: center;
    margin-bottom: 1rem;
}
.app-title-wrap h1 {
    margin: 0 0 0.5rem 0;
    font-weight: 700;
    font-size: 1.75rem;
    line-height: 1.25;
}
/* Intro y banner de estado: ancho cómodo, alineados a la izquierda dentro del panel principal */
.app-main-with-sidebar .app-intro,
.app-main-with-sidebar .app-settings-banner {
    max-width: 52rem;
    margin-left: 0 !important;
    margin-right: auto !important;
}
.app-model-sidebar .app-footer-note {
    max-width: 100% !important;
    margin-left: 0 !important;
    margin-right: 0 !important;
    margin-top: 0.75rem !important;
    padding-top: 0.65rem !important;
    border-top: 1px solid rgba(55, 75, 95, 0.12) !important;
}
.relato-input textarea,
.relato-input .scroll-hide,
.relato-input input,
.relato-input [data-testid="textbox"] {
    background-color: #ffffff !important;
}
.relato-input .wrap,
.relato-input .block {
    background-color: #ffffff !important;
}
.app-version {
    text-align: center;
    font-size: 0.7rem;
    line-height: 1.4;
    color: rgba(45, 65, 88, 0.45);
    margin: 0.35rem 0 0 0;
    letter-spacing: 0.04em;
    font-weight: 500;
    user-select: none;
}
.relato-col-heading {
    display: flex;
    align-items: center;
    gap: 0.45rem;
    margin: 0 0 0.65rem 0;
    font-size: 1rem;
    font-weight: 600;
    line-height: 1.35;
}
.relato-col-heading .red-pennant-svg {
    flex-shrink: 0;
    display: block;
}
.relato-col-body {
    margin: 0;
    line-height: 1.55;
}
.relato-col-body strong {
    font-weight: 600;
}
/* Fila principal: barra lateral alineada arriba con la primera línea del texto introductorio */
.app-body-layout {
    align-items: flex-start !important;
    flex-wrap: nowrap !important;
}
.app-body-layout .app-model-sidebar,
.app-body-layout .app-main-with-sidebar {
    align-self: flex-start !important;
    padding-top: 0 !important;
    margin-top: 0 !important;
}
.app-model-sidebar {
    flex: 0 0 auto !important;
    min-width: 12rem !important;
    max-width: 17rem !important;
    padding: 0 1.1rem 0 0 !important;
    margin-right: 0.25rem !important;
    border-right: 1px solid rgba(55, 75, 95, 0.18) !important;
}
.app-main-with-sidebar {
    flex: 1 1 auto !important;
    min-width: 0 !important;
}
.app-model-sidebar .form,
.app-main-with-sidebar .form,
.app-relato-col .form {
    padding-top: 0 !important;
    margin-top: 0 !important;
    gap: 0.5rem !important;
}
/* Primera línea "Motor de LLM" = misma tipografía base que el primer párrafo del intro */
.app-body-layout .app-sidebar-motor .prose > p:first-child {
    margin-top: 0 !important;
    margin-bottom: 0.65rem !important;
    font-size: inherit !important;
    font-weight: inherit !important;
    line-height: inherit !important;
}
.app-body-layout .app-main-with-sidebar .app-intro .prose > p:first-child {
    margin-top: 0 !important;
}
.app-body-layout .app-sidebar-motor .prose,
.app-body-layout .app-sidebar-motor .prose p {
    font-size: inherit !important;
    line-height: inherit !important;
}
.app-model-sidebar .app-footer-note .prose,
.app-model-sidebar .app-footer-note p {
    font-size: 0.88rem !important;
    line-height: 1.45 !important;
}
.app-workbench {
    margin-top: 0.35rem !important;
    flex-direction: column !important;
    flex-wrap: nowrap !important;
    align-items: stretch !important;
    gap: 0 !important;
}
.app-workbench .app-workbench-row {
    align-items: stretch !important;
    flex-wrap: nowrap !important;
    margin: 0 !important;
}
.app-workbench .app-workbench-row + .app-workbench-row {
    margin-top: 0.65rem !important;
}
.app-workbench .app-workbench-row.app-workbench-inputs {
    margin-top: 0.5rem !important;
    align-items: flex-start !important;
}
.app-workbench .app-relato-cell {
    min-width: 0 !important;
    padding-top: 0 !important;
    margin-top: 0 !important;
}
.app-workbench .app-relato-cell .block {
    padding-top: 0 !important;
}
.app-relato-col {
    align-self: flex-start !important;
    padding-top: 0 !important;
    margin-top: 0 !important;
}
.app-relato-col-left .relato-col-intro {
    margin: 0 !important;
    padding: 0 !important;
}
.relato-heading-spacer {
    flex-shrink: 0;
    width: 20px;
    height: 26px;
    display: block;
}
.app-model-sidebar .block,
.app-relato-col .block,
.app-main-with-sidebar .block {
    padding-top: 0 !important;
}
.app-main-actions {
    padding-top: 0.75rem !important;
    max-width: 100% !important;
}
.analysis-pending-line {
    margin: 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 1.05rem;
    font-weight: 600;
    color: rgba(35, 55, 80, 0.92);
}
.analysis-pending-spinner {
    flex-shrink: 0;
    width: 1.1rem;
    height: 1.1rem;
    border: 2.5px solid rgba(45, 90, 140, 0.22);
    border-top-color: rgba(30, 100, 180, 0.95);
    border-radius: 50%;
    animation: analysis-pending-spin 0.65s linear infinite;
}
@keyframes analysis-pending-spin {
    to {
        transform: rotate(360deg);
    }
}
@media (max-width: 768px) {
    .app-body-layout {
        flex-wrap: wrap !important;
    }
    .app-workbench .app-workbench-row {
        flex-wrap: wrap !important;
    }
    .app-model-sidebar {
        max-width: 100% !important;
        border-right: none !important;
        border-bottom: 1px solid rgba(55, 75, 95, 0.18) !important;
        padding-bottom: 0.85rem !important;
        margin-bottom: 0.5rem !important;
    }
}
"""


def get_pipeline() -> ProtestPipeline:
    global _pipeline
    with _pipeline_lock:
        if _pipeline is None:
            _pipeline = ProtestPipeline.from_env()
        return _pipeline


def _warm_pipeline_async() -> None:
    def _run() -> None:
        try:
            if activity_console_enabled():
                log_note("Precalentando índice del corpus en segundo plano…")
            get_pipeline()
            if activity_console_enabled():
                log_note("Índice listo.")
        except Exception as exc:
            if activity_console_enabled():
                log_note(f"Precalentado omitido: {exc!r}")

    threading.Thread(target=_run, name="regatas-pipeline-warmup", daemon=True).start()


def analyze(
    relato_protesta: str,
    relato_protestado: str,
    idioma_system_prompt: str | None,
    estrategia_prompt: str | None,
    ollama_model: str | None,
) -> Iterator[str]:
    """Generador: primer chunk = espera; la consola externa se actualiza en paralelo."""
    if relato_protesta is None or not str(relato_protesta).strip():
        yield "**Error:** el relato del **barco que protesta** es obligatorio."
        return
    clear_for_new_query()
    if activity_console_enabled():
        log_note("Nueva consulta.")
    s = Settings.from_env()
    pending = _ANALYSIS_PENDING_HTML if s.llm_backend != "stub" else ""
    if pending:
        yield pending
    try:
        if _pipeline is None:
            log_note(
                "Cargando índice del corpus (primera vez puede tardar varios minutos "
                f"si REGATAS_EMBEDDING_BACKEND={s.embedding_backend})…"
            )
        p = get_pipeline()
        if s.llm_backend == "http":
            log_note(
                f"Esperando respuesta del LLM (timeout {int(s.llm_timeout_seconds)} s)…"
            )
        second = relato_protestado if relato_protestado else ""
        second = second.strip() or None
        spl = (idioma_system_prompt or "").strip() or None
        strat = (estrategia_prompt or "").strip() or None
        llm_model: str | None = None
        if s.llm_backend == "http":
            om = (ollama_model or "").strip()
            llm_model = om or None
        yield p.analyze(
            str(relato_protesta).strip(),
            second,
            system_prompt_lang=spl,
            prompt_strategy=strat,
            llm_model=llm_model,
        )
    except FileNotFoundError as e:
        yield f"**Falta corpus**\n\n{e}\n\nSubí los PDF del Call Book y Case Book a la carpeta `corpus/` del proyecto (o ajustá `REGATAS_BASE_DIR` y, si aplica, `REGATAS_CORPUS_SUBDIR`)."
    except Exception as e:
        yield f"**Error**\n\n```\n{e!r}\n```"


def _settings_banner() -> str:
    s = Settings.from_env()
    lines = [
        "Estado actual del motor (útil para depuración y para saber si ya configuraste APIs o modelos remotos):",
        f"- **Recuperación de contexto:** modo `{s.embedding_backend}` · se muestran hasta **{s.retrieve_top_k}** fragmentos del corpus en cada consulta.",
        f"- **Modelo de lenguaje:** backend `{s.llm_backend}`.",
        f"- **System prompt (default env):** idioma `{s.system_prompt_language}` (`REGATAS_SYSTEM_PROMPT_LANG=es|en`), estrategia `{s.prompt_strategy}` (`REGATAS_PROMPT_STRATEGY=cot|few_shot_cot`). El informe sigue redactándose en español.",
    ]
    if s.llm_backend == "http":
        lines.append(f"- **Modelo LLM:** `{s.llm_model}` (`REGATAS_LLM_MODEL`).")
        if s.llm_base_url:
            lines.append(f"- **Base URL (API compatible):** `{s.llm_base_url}`.")
        else:
            lines.append("- **Base URL:** *(default del cliente HTTP / no definida)*.")
    if is_huggingface_space():
        lines.insert(1, "- **Entorno:** Hugging Face Space (secretos en *Settings → Secrets*).")
    return "\n".join(lines)


def _ollama_dropdown_updates() -> tuple[dict, dict]:
    """Actualiza desplegable de modelos y mensaje de ayuda según Ollama y el entorno."""
    s = Settings.from_env()
    if s.llm_backend != "http":
        return (
            gr.update(visible=False),
            gr.update(value="", visible=False),
        )
    installed = list_installed_ollama_models(s.llm_base_url)
    if installed:
        value = ollama_default_choice(installed, s.llm_model)
        return (
            gr.update(
                choices=installed,
                value=value,
                visible=True,
                interactive=True,
            ),
            gr.update(value="", visible=True),
        )
    hint = (
        "*No se pudo obtener la lista de modelos desde Ollama* (`/api/tags`). "
        "Comprobá que el servicio esté en marcha y que `REGATAS_LLM_BASE_URL` apunte a la API compatible "
        "(p. ej. `http://127.0.0.1:11434/v1`). Mientras tanto se usa el modelo del entorno "
        f"`REGATAS_LLM_MODEL` = `{s.llm_model}`."
    )
    return (
        gr.update(
            choices=[s.llm_model],
            value=s.llm_model,
            visible=True,
            interactive=True,
        ),
        gr.update(value=hint, visible=True),
    )


def build_app() -> gr.Blocks:
    _s0 = Settings.from_env()
    _spl_def = (
        _s0.system_prompt_language
        if _s0.system_prompt_language in ("es", "en")
        else "es"
    )
    _strat_def = (
        _s0.prompt_strategy
        if _s0.prompt_strategy in ("cot", "few_shot_cot")
        else "cot"
    )
    _ollama_installed = (
        list_installed_ollama_models(_s0.llm_base_url)
        if _s0.llm_backend == "http"
        else []
    )
    _ollama_choices = (
        _ollama_installed
        if _ollama_installed
        else ([_s0.llm_model] if _s0.llm_backend == "http" else [])
    )
    _ollama_value = (
        ollama_default_choice(_ollama_installed, _s0.llm_model)
        if _ollama_installed
        else _s0.llm_model
    )
    _ollama_show = _s0.llm_backend == "http"
    _ollama_hint_init = ""
    if _ollama_show and not _ollama_installed:
        _ollama_hint_init = (
            "*No se pudo obtener la lista de modelos desde Ollama* (`/api/tags`). "
            "Comprobá que el servicio esté en marcha. Mientras tanto se usa el modelo del entorno "
            f"`REGATAS_LLM_MODEL` = `{_s0.llm_model}`."
        )
    # css/theme en Blocks: el `demo` exportado conserva el estilo si el host llama a launch() sin kwargs (p. ej. HF Spaces).
    with gr.Blocks(
        title="Asistente de protestas — Team Racing (PoC)",
        theme=gr.themes.Soft(),
        css=_PAGE_CSS,
    ) as demo:
        with gr.Column(elem_classes=["app-header"]):
            if _HERO_IMAGE.is_file():
                gr.Image(
                    value=str(_HERO_IMAGE),
                    type="filepath",
                    label="Regatas a vela — imagen decorativa del encabezado",
                    show_label=False,
                    interactive=False,
                    container=False,
                    buttons=[],
                    elem_classes=["app-hero-banner"],
                    height=200,
                )
            gr.HTML(
                '<div class="app-title-wrap">'
                "<h1>Asistente de protestas en regatas (PoC)</h1>"
                "</div>"
            )
        with gr.Row(equal_height=False, elem_classes=["app-body-layout"]):
            with gr.Column(scale=0, min_width=200, elem_classes=["app-model-sidebar"]):
                gr.Markdown(
                    "**Motor de LLM**\n\n"
                    "En local, con `REGATAS_LLM_BACKEND=http`, la app habla con **Ollama** por la API HTTP compatible "
                    "(`http://127.0.0.1:11434/v1` por defecto). El **modelo activo** lo elegís del desplegable: "
                    "solo aparecen los que Ollama tiene instalados (`ollama list`). "
                    "La URL y el modelo por defecto del entorno siguen en `REGATAS_LLM_BASE_URL` y `REGATAS_LLM_MODEL` "
                    "(o las variables legacy documentadas en `.env.example`).\n\n"
                    "Con `REGATAS_LLM_BACKEND=stub` verás solo una respuesta de demostración. "
                    "El valor legacy `openai` se acepta como alias de `http`.",
                    elem_classes=["app-sidebar-motor"],
                )
                ollama_models_hint = gr.Markdown(
                    value=_ollama_hint_init,
                    visible=_ollama_show,
                    elem_classes=["app-ollama-hint"],
                )
                ollama_model_dd = gr.Dropdown(
                    choices=_ollama_choices if _ollama_choices else [_s0.llm_model],
                    value=_ollama_value,
                    label="Modelo Ollama (local)",
                    show_label=True,
                    visible=_ollama_show,
                    interactive=_ollama_show,
                    allow_custom_value=False,
                )
                refresh_ollama = gr.Button(
                    "Actualizar lista de modelos",
                    visible=_ollama_show,
                    size="sm",
                )
                gr.Markdown(
                    "El **system prompt** puede ir en español o en inglés; el **informe** sigue en español. "
                    "Elegí también la **estrategia de prompt** (Chain-of-Thought explícito vs Few-Shot CoT con ranura de ejemplos). "
                    "Defaults: `REGATAS_SYSTEM_PROMPT_LANG` y `REGATAS_PROMPT_STRATEGY`.",
                    elem_classes=["app-sidebar-motor"],
                )
                lang_system_poc = gr.Radio(
                    choices=[("Español", "es"), ("English", "en")],
                    value=_spl_def,
                    label="Idioma del system prompt",
                    show_label=True,
                )
                prompt_strategy_poc = gr.Radio(
                    choices=[
                        ("Chain-of-Thought (CoT explícito)", "cot"),
                        ("Few-Shot Chain-of-Thought", "few_shot_cot"),
                    ],
                    value=_strat_def,
                    label="Estrategia de prompt",
                    show_label=True,
                )
                gr.Markdown(
                    "**Configuración avanzada.** "
                    "Podés cambiar el modo de búsqueda en el corpus con `REGATAS_EMBEDDING_BACKEND` "
                    "(`lexical` sin API, `http` o `local` con modelo de embeddings) y el generador de texto con "
                    "`REGATAS_LLM_BACKEND`: en local el default es `http` contra **Ollama** (`REGATAS_LLM_BASE_URL`, "
                    "`REGATAS_LLM_MODEL=llama3`, `REGATAS_LLM_API_KEY=ollama`). Las variables legacy del `.env.example` siguen funcionando. "
                    "Usá `stub` para demo sin LLM. "
                    "En **Hugging Face Spaces** el default es `stub` salvo que configures API remota y secretos. "
                    "`REGATAS_SYSTEM_PROMPT_LANG` (`es`/`en`), `REGATAS_PROMPT_STRATEGY` (`cot`/`few_shot_cot`) y los selectores en la barra lateral ajustan el system prompt. "
                    "El archivo `.env.example` del repositorio resume el resto de variables.",
                    elem_classes=["app-footer-note"],
                )
            with gr.Column(scale=1, elem_classes=["app-main-with-sidebar"]):
                gr.Markdown(
                    "Esta herramienta apoya la **resolución de protestas en regatas por equipos (Team Racing)** "
                    "a partir de relatos en lenguaje cotidiano. El motor localiza pasajes relevantes del "
                    "*Call Book for Team Racing* y del *Case Book* de World Sailing, los combina con tu relato "
                    "y produce un **informe en cuatro partes**: hechos, normas y Calls priorizados, razonamiento técnico y dictamen sugerido. "
                    "No sustituye al comité de protesta: sirve para **acelerar el análisis** y **documentar el razonamiento**.\n\n"
                    "Debajo hay **dos columnas de relatos**: "
                    "a la **izquierda** el relato del barco que **presenta la protesta** (obligatorio); "
                    "a la **derecha**, si lo conocés, la versión del **barco protestado** (opcional). "
                    "Si hay dos versiones, el asistente intentará **separar hechos coincidentes de contradicciones** "
                    "y aplicar el criterio del *último punto de certeza* descrito en la consigna del trabajo.",
                    elem_classes=["app-intro"],
                )
                gr.Markdown(_settings_banner(), elem_classes=["app-settings-banner"])
                with gr.Column(elem_classes=["app-workbench"]):
                    with gr.Row(equal_height=True, elem_classes=["app-workbench-row"]):
                        with gr.Column(
                            scale=1,
                            elem_classes=["app-relato-col", "app-relato-cell", "app-relato-col-left"],
                        ):
                            gr.HTML(
                                '<p class="relato-col-heading">'
                                '<svg class="red-pennant-svg" xmlns="http://www.w3.org/2000/svg" '
                                'viewBox="0 0 28 36" width="20" height="26" role="img" '
                                'aria-label="Banderín rojo de protesta">'
                                '<rect x="1" y="2" width="2.5" height="32" fill="#4a3728" rx="0.5"/>'
                                '<path d="M6 5 L26 18 L6 31 Z" fill="#d61f2a"/>'
                                "</svg>"
                                "<span>Barco que protesta</span>"
                                "</p>"
                            )
                        with gr.Column(
                            scale=1,
                            elem_classes=["app-relato-col", "app-relato-cell", "app-relato-col-right"],
                        ):
                            gr.HTML(
                                '<p class="relato-col-heading">'
                                '<span class="relato-heading-spacer" aria-hidden="true"></span>'
                                "<span>Barco protestado</span>"
                                "</p>"
                            )
                    with gr.Row(equal_height=True, elem_classes=["app-workbench-row"]):
                        with gr.Column(
                            scale=1,
                            elem_classes=["app-relato-col", "app-relato-cell", "app-relato-col-left"],
                        ):
                            gr.HTML(
                                '<div class="relato-col-intro">'
                                "<p class=\"relato-col-body\">Quien inicia la protesta cuenta <strong>qué vio y qué hizo cada barco</strong>, "
                                "en el orden que recuerde (pre-salida, ceñida, popa, boya, contacto, etc.). "
                                "Mientras más preciso sea el relato (amuras, barlovento/sotavento, quién orzó o panó), mejor será el análisis.</p>"
                                "</div>"
                            )
                        with gr.Column(
                            scale=1,
                            elem_classes=["app-relato-col", "app-relato-cell", "app-relato-col-right"],
                        ):
                            gr.HTML(
                                '<div class="relato-col-intro">'
                                "<p class=\"relato-col-body\">Si tenés la <strong>versión del otro equipo</strong>, pegala en el cuadro de abajo. "
                                "Si no hay segunda versión, podés dejarlo vacío: el sistema trabajará solo con el relato de la protesta.</p>"
                                "</div>"
                            )
                    with gr.Row(equal_height=False, elem_classes=["app-workbench-row", "app-workbench-inputs"]):
                        with gr.Column(
                            scale=1,
                            elem_classes=["app-relato-col", "app-relato-cell", "app-relato-col-left"],
                        ):
                            relato_p = gr.Textbox(
                                label="Relato",
                                show_label=False,
                                placeholder="Descripción del incidente desde quien presenta la protesta…",
                                lines=14,
                                elem_id="relato-protesta",
                                elem_classes=["relato-input"],
                            )
                        with gr.Column(
                            scale=1,
                            elem_classes=["app-relato-col", "app-relato-cell", "app-relato-col-right"],
                        ):
                            relato_d = gr.Textbox(
                                label="Relato",
                                show_label=False,
                                placeholder="Versión del otro involucrado, si la tenés…",
                                lines=14,
                                elem_id="relato-protestado",
                                elem_classes=["relato-input"],
                            )
                with gr.Column(elem_classes=["app-main-actions"]):
                    run = gr.Button("Analizar incidente", variant="primary")
                    out = gr.Markdown(sanitize_html=False)
        run.click(
            fn=analyze,
            inputs=[
                relato_p,
                relato_d,
                lang_system_poc,
                prompt_strategy_poc,
                ollama_model_dd,
            ],
            outputs=out,
            show_progress="full",
            show_progress_on=[run, out],
        )
        refresh_ollama.click(
            fn=_ollama_dropdown_updates,
            outputs=[ollama_model_dd, ollama_models_hint],
        )
        demo.load(
            fn=_ollama_dropdown_updates,
            outputs=[ollama_model_dd, ollama_models_hint],
        )
        gr.HTML(
            f'<p class="app-version" aria-label="Versión {__version__}">v{__version__}</p>'
        )
    return demo


demo = build_app()


if __name__ == "__main__":
    if launch_on_startup(in_space=is_huggingface_space()):
        print("Consola de actividad: ventana independiente abierta.")
    elif not is_huggingface_space() and not activity_console_enabled():
        print(
            "Consola desactivada (REGATAS_ACTIVITY_CONSOLE=0). "
            "Para omitir la ventana al arrancar, usá esa variable."
        )
    if os.environ.get("REGATAS_PRELOAD_PIPELINE", "1").strip().lower() not in (
        "0",
        "false",
        "no",
        "off",
    ):
        _warm_pipeline_async()
    port = int(os.environ.get("PORT", "7860"))
    demo.launch(
        server_name="0.0.0.0",
        server_port=port,
        allowed_paths=[str(ROOT)],
    )
