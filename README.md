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

## Secretos (Settings → Secrets)

| Variable | Uso |
|----------|-----|
| `OPENAI_API_KEY` | Si usás `REGATAS_LLM_BACKEND=openai` y/o `REGATAS_EMBEDDING_BACKEND=openai` |
| `OPENAI_BASE_URL` | Opcional (Azure, proxy compatible) |
| `OPENAI_LLM_MODEL` | Opcional, default `gpt-4o-mini` |
| `REGATAS_LLM_BACKEND` | `stub` (default) o `openai` |
| `REGATAS_EMBEDDING_BACKEND` | `lexical` (default, rápido), `openai` o `local` |

Para embeddings **local** en CPU hace falta ampliar `requirements.txt` con `sentence-transformers` (y `torch`); el arranque será más lento.

## Local

```bash
pip install -r requirements.txt
python app.py
```

Copiá `.env.example` a `.env` si usás un gestor de variables en tu IDE.
