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

from regatas_assistant.config import Settings, is_huggingface_space
from regatas_assistant.pipeline import ProtestPipeline

_pipeline: ProtestPipeline | None = None

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
"""


def get_pipeline() -> ProtestPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = ProtestPipeline.from_env()
    return _pipeline


def analyze(relato_protesta: str, relato_protestado: str) -> str:
    if relato_protesta is None or not str(relato_protesta).strip():
        return "**Error:** el relato del **barco que protesta** es obligatorio."
    try:
        p = get_pipeline()
        second = relato_protestado if relato_protestado else ""
        second = second.strip() or None
        return p.analyze(str(relato_protesta).strip(), second)
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
        lines.append(f"- **Modelo de chat:** `{s.openai_llm_model}`.")
    if is_huggingface_space():
        lines.insert(1, "- **Entorno:** Hugging Face Space (secretos en *Settings → Secrets*).")
    return "\n".join(lines)


def build_app() -> gr.Blocks:
    # css/theme en Blocks: el `demo` exportado conserva el estilo si el host llama a launch() sin kwargs (p. ej. HF Spaces).
    with gr.Blocks(
        title="Asistente de protestas — Team Racing (PoC)",
        theme=gr.themes.Soft(),
        css=_PAGE_CSS,
    ) as demo:
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
            "Debajo tenés **dos columnas**: a la **izquierda** el relato del barco que **presenta la protesta** (obligatorio); "
            "a la **derecha**, si lo conocés, la versión del **barco protestado** (opcional). "
            "Si hay dos versiones, el asistente intentará **separar hechos coincidentes de contradicciones** "
            "y aplicar el criterio del *último punto de certeza* descrito en la consigna del trabajo.",
            elem_classes=["app-intro"],
        )
        gr.Markdown(_settings_banner(), elem_classes=["app-settings-banner"])
        with gr.Row(equal_height=True):
            with gr.Column(scale=1):
                gr.Markdown(
                    "**Columna izquierda — barco que protesta**\n\n"
                    "Quien inicia la protesta cuenta **qué vio y qué hizo cada barco**, "
                    "en el orden que recuerde (pre-salida, ceñida, popa, boya, contacto, etc.). "
                    "Mientras más preciso sea el relato (amuras, barlovento/sotavento, quién orzó o panó), mejor será el análisis."
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
                    "**Columna derecha — barco protestado (opcional)**\n\n"
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
        run.click(fn=analyze, inputs=[relato_p, relato_d], outputs=out)
        gr.Markdown(
            "**Configuración avanzada.** "
            "Podés cambiar el modo de búsqueda en el corpus con `REGATAS_EMBEDDING_BACKEND` "
            "(`lexical` sin API, `openai` o `local` con modelo de embeddings) y el generador de texto con "
            "`REGATAS_LLM_BACKEND` (`stub` para pruebas sin API, `openai` para un modelo vía API compatible). "
            "En **Hugging Face Spaces**, definí esos valores y la clave `OPENAI_API_KEY` (u otras) en *Secrets*. "
            "El archivo `.env.example` del repositorio resume el resto de variables.",
            elem_classes=["app-footer-note"],
        )
    return demo


demo = build_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "7860"))
    demo.launch(server_name="0.0.0.0", server_port=port)
