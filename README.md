---
title: Asistente protestas regatas (PoC)
emoji: ⛵
colorFrom: slate
colorTo: blue
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
---

# Asistente de protestas — Team Racing (PoC)

Subí a la raíz del Space los PDF:

- `The-Call-Book-for-Team-Racing-2025-2028.pdf`
- `WS-Case-Book-2025-2028-v2025-07.pdf`

## Local (Ollama + Llama 3)

1. Instalá [Ollama](https://ollama.com) y ejecutá `ollama pull llama3`.
2. Dejá el servidor en marcha (por defecto escucha en el puerto 11434).
3. Sin variables extra, la app usa la API HTTP de chat en `http://127.0.0.1:11434/v1`, modelo `llama3` y clave dummy `ollama`.

| Variable | Uso (local típico) |
|----------|-------------------|
| `REGATAS_LLM_BACKEND` | `http` (default fuera de HF Space), alias legacy `openai`, o `stub` para demo sin LLM |
| `REGATAS_LLM_BASE_URL` | Default `http://127.0.0.1:11434/v1` (Ollama) |
| `REGATAS_LLM_API_KEY` | Default `ollama` si no definís otra |
| `REGATAS_LLM_MODEL` | Default `llama3` (debe existir en Ollama, p. ej. `llama3.1` si preferís) |
| `REGATAS_EMBEDDING_BACKEND` | `lexical` (default), `http` (alias legacy `openai`) o `local` |
| `REGATAS_EMBEDDING_MODEL` | Modelo de embeddings si `REGATAS_EMBEDDING_BACKEND=http` (default `text-embedding-3-small`) |

*Compatibilidad:* si no definís las equivalentes `REGATAS_*`, se leen las variables alternativas documentadas en `.env.example`.

## Hugging Face Space (secretos)

En Space no hay Ollama: el default es `REGATAS_LLM_BACKEND=stub` hasta que configures una API remota.

| Variable | Uso |
|----------|-----|
| `REGATAS_LLM_API_KEY` | Necesaria si usás `REGATAS_LLM_BACKEND=http` contra un host remoto compatible |
| `REGATAS_LLM_BASE_URL` | Opcional (URL base del proveedor o proxy) |
| `REGATAS_LLM_MODEL` | Modelo remoto (en Space el default es `gpt-4o-mini` si no definís variable) |
| `REGATAS_LLM_BACKEND` | `http` o `stub` |
| `REGATAS_EMBEDDING_BACKEND` | `lexical` (default), `http` o `local` |

Para embeddings **local** en CPU hace falta ampliar `requirements.txt` con `sentence-transformers` (y `torch`); el arranque será más lento.

## Local

```bash
pip install -r requirements.txt
python app.py
```

Copiá `.env.example` a `.env` si usás un gestor de variables en tu IDE.
