"""
Interfaz Gradio del asistente de protestas.
Ejecución local: `python app.py`
Hugging Face Space: SDK Gradio; asegurate de subir los PDF del corpus y definir secretos (p. ej. OPENAI_API_KEY).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import gradio as gr

from regatas_assistant import __version__
from regatas_assistant.config import Settings, is_huggingface_space
from regatas_assistant.pipeline import ProtestPipeline

_pipeline: ProtestPipeline | None = None

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
.app-intro, .app-footer-note, .app-settings-banner {
    max-width: 52rem;
    margin-left: auto;
    margin-right: auto;
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
.app-workbench {
    align-items: flex-start !important;
    flex-wrap: nowrap !important;
}
.app-model-sidebar {
    flex: 0 0 auto !important;
    min-width: 12rem !important;
    max-width: 17rem !important;
    padding: 0.35rem 1.1rem 1rem 0 !important;
    margin-right: 0.25rem !important;
    border-right: 1px solid rgba(55, 75, 95, 0.18) !important;
}
.app-model-sidebar .prose, .app-model-sidebar p {
    font-size: 0.88rem !important;
    line-height: 1.45 !important;
}
.app-main-tool {
    flex: 1 1 auto !important;
    min-width: 0 !important;
}
@media (max-width: 768px) {
    .app-workbench {
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


def _ui_llm_model_choices() -> tuple[list[str], str]:
    """Opciones y valor por defecto del Radio (incluye siempre OPENAI_LLM_MODEL)."""
    s = Settings.from_env()
    merged = list(dict.fromkeys([s.openai_llm_model, *s.llm_model_choices]))
    default = (
        s.openai_llm_model
        if s.openai_llm_model in merged
        else (merged[0] if merged else "")
    )
    return merged, default


def get_pipeline() -> ProtestPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = ProtestPipeline.from_env()
    return _pipeline


def analyze(
    relato_protesta: str,
    relato_protestado: str,
    modelo_llm: str | None,
) -> str:
    if relato_protesta is None or not str(relato_protesta).strip():
        return "**Error:** el relato del **barco que protesta** es obligatorio."
    try:
        p = get_pipeline()
        second = relato_protestado if relato_protestado else ""
        second = second.strip() or None
        m = (modelo_llm or "").strip() or None
        return p.analyze(
            str(relato_protesta).strip(),
            second,
            llm_model=m,
        )
    except FileNotFoundError as e:
        return f"**Falta corpus**\n\n{e}\n\nSubí los PDF del Call Book y Case Book a la raíz del proyecto o ajustá `REGATAS_BASE_DIR`."
    except Exception as e:
        return f"**Error**\n\n```\n{e!r}\n```"


def _settings_banner() -> str:
    s = Settings.from_env()
    lines = [
        "Estado actual del motor (útil para depuración y para saber si ya configuraste APIs o modelos remotos):",
        f"- **Recuperación de contexto:** modo `{s.embedding_backend}` · se muestran hasta **{s.retrieve_top_k}** fragmentos del corpus en cada consulta.",
        f"- **Modelo de lenguaje:** backend `{s.llm_backend}`.",
    ]
    if s.llm_backend == "openai":
        lines.append(f"- **Modelo de chat (default env):** `{s.openai_llm_model}`.")
        lines.append(
            "- **Modelos disponibles (barra lateral):** "
            + ", ".join(f"`{m}`" for m in dict.fromkeys([s.openai_llm_model, *s.llm_model_choices]))
            + " — personalizá la lista con `REGATAS_LLM_MODEL_CHOICES`."
        )
    if is_huggingface_space():
        lines.insert(1, "- **Entorno:** Hugging Face Space (secretos en *Settings → Secrets*).")
    return "\n".join(lines)


def build_app() -> gr.Blocks:
    poc_choices, poc_default = _ui_llm_model_choices()
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
        gr.Markdown(
            "Esta herramienta apoya la **resolución de protestas en regatas por equipos (Team Racing)** "
            "a partir de relatos en lenguaje cotidiano. El motor localiza pasajes relevantes del "
            "*Call Book for Team Racing* y del *Case Book* de World Sailing, los combina con tu relato "
            "y produce un **informe en cuatro partes**: hechos, normas y Calls priorizados, razonamiento técnico y dictamen sugerido. "
            "No sustituye al comité de protesta: sirve para **acelerar el análisis** y **documentar el razonamiento**.\n\n"
            "En el **panel principal** (junto a la barra de modelo) hay **dos columnas de relatos**: "
            "a la **izquierda** el relato del barco que **presenta la protesta** (obligatorio); "
            "a la **derecha**, si lo conocés, la versión del **barco protestado** (opcional). "
            "Si hay dos versiones, el asistente intentará **separar hechos coincidentes de contradicciones** "
            "y aplicar el criterio del *último punto de certeza* descrito en la consigna del trabajo.",
            elem_classes=["app-intro"],
        )
        gr.Markdown(_settings_banner(), elem_classes=["app-settings-banner"])
        with gr.Row(equal_height=False, elem_classes=["app-workbench"]):
            with gr.Column(scale=0, min_width=200, elem_classes=["app-model-sidebar"]):
                gr.Markdown(
                    "**Modelo LLM** (PoC)\n\n"
                    "Elegí **un solo** modelo por análisis. El mismo contexto RAG se usa siempre; "
                    "solo cambia el modelo que redacta el informe.\n\n"
                    "Con `REGATAS_LLM_BACKEND=stub` la elección no afecta la respuesta de demostración. "
                    "Para **Ollama** u otro endpoint compatible, configurá los nombres en `REGATAS_LLM_MODEL_CHOICES`.",
                )
                model_poc = gr.Radio(
                    choices=poc_choices,
                    value=poc_default if poc_default else None,
                    label="Modelo activo",
                    show_label=True,
                )
            with gr.Column(scale=1, elem_classes=["app-main-tool"]):
                with gr.Row(equal_height=True):
                    with gr.Column(scale=1):
                        gr.HTML(
                            '<div class="relato-col-intro">'
                            '<p class="relato-col-heading">'
                            '<svg class="red-pennant-svg" xmlns="http://www.w3.org/2000/svg" '
                            'viewBox="0 0 28 36" width="20" height="26" role="img" '
                            'aria-label="Banderín rojo de protesta">'
                            '<rect x="1" y="2" width="2.5" height="32" fill="#4a3728" rx="0.5"/>'
                            '<path d="M6 5 L26 18 L6 31 Z" fill="#d61f2a"/>'
                            "</svg>"
                            "<span>Barco que protesta</span>"
                            "</p>"
                            "<p class=\"relato-col-body\">Quien inicia la protesta cuenta <strong>qué vio y qué hizo cada barco</strong>, "
                            "en el orden que recuerde (pre-salida, ceñida, popa, boya, contacto, etc.). "
                            "Mientras más preciso sea el relato (amuras, barlovento/sotavento, quién orzó o panó), mejor será el análisis.</p>"
                            "</div>"
                        )
                        relato_p = gr.Textbox(
                            label="Relato",
                            show_label=False,
                            placeholder="Descripción del incidente desde quien presenta la protesta…",
                            lines=14,
                            elem_id="relato-protesta",
                            elem_classes=["relato-input"],
                        )
                    with gr.Column(scale=1):
                        gr.Markdown(
                            "**Barco Protestado**\n\n"
                            "Si tenés la **versión del otro equipo**, pegala aquí. "
                            "Si no hay segunda versión, podés dejar este cuadro vacío: el sistema trabajará solo con el relato de la protesta."
                        )
                        relato_d = gr.Textbox(
                            label="Relato",
                            show_label=False,
                            placeholder="Versión del otro involucrado, si la tenés…",
                            lines=14,
                            elem_id="relato-protestado",
                            elem_classes=["relato-input"],
                        )
                run = gr.Button("Analizar incidente", variant="primary")
                out = gr.Markdown()
        run.click(
            fn=analyze,
            inputs=[relato_p, relato_d, model_poc],
            outputs=out,
        )
        gr.Markdown(
            "**Configuración avanzada.** "
            "Podés cambiar el modo de búsqueda en el corpus con `REGATAS_EMBEDDING_BACKEND` "
            "(`lexical` sin API, `openai` o `local` con modelo de embeddings) y el generador de texto con "
            "`REGATAS_LLM_BACKEND` (`stub` para pruebas sin API, `openai` para un modelo vía API compatible). "
            "Los modelos de la barra lateral se arman con `REGATAS_LLM_MODEL_CHOICES` (coma-separada) "
            "y siempre incluyen `OPENAI_LLM_MODEL`. "
            "En **Hugging Face Spaces**, definí esos valores y la clave `OPENAI_API_KEY` (u otras) en *Secrets*. "
            "El archivo `.env.example` del repositorio resume el resto de variables.",
            elem_classes=["app-footer-note"],
        )
        gr.HTML(
            f'<p class="app-version" aria-label="Versión {__version__}">v{__version__}</p>'
        )
    return demo


demo = build_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "7860"))
    demo.launch(
        server_name="0.0.0.0",
        server_port=port,
        allowed_paths=[str(ROOT)],
    )
