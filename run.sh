#!/usr/bin/env bash
# Arranque local de la PoC (Gradio + consola de actividad).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

if [[ ! -d .venv ]]; then
  echo "No se encontró .venv. Creá el entorno e instalá dependencias:"
  echo "  python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
  exit 1
fi

# shellcheck disable=SC1091
source .venv/bin/activate

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

export PORT="${PORT:-7860}"

echo "Verificando RAG, configuración y Ollama…"
if ! python3 scripts/check_setup.py --skip-llm; then
  echo ""
  echo "Corregí los problemas anteriores antes de continuar."
  echo "Para probar también el LLM: python3 scripts/check_setup.py"
  exit 1
fi
echo ""

if lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Puerto $PORT ocupado; probando 7861…"
  export PORT=7861
fi

echo "Iniciando asistente en http://127.0.0.1:$PORT"
echo "(La primera carga puede tardar varios minutos si el .venv está en OneDrive.)"
exec python3 app.py
