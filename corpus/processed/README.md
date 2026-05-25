# Corpus pre-procesado (JSONL)

Artefactos generados desde los CSV estructurados del RRS. **No editar a mano** los `.jsonl`; regenerar con el script.

## Generar

```bash
python scripts/build_corpus_processed.py
```

Fuentes:

- `scripts/rrs_reglas_2025_2028.csv` → `rrs_rules.jsonl` (un chunk por regla/subregla)
- `scripts/definitions.csv` → `definitions.jsonl` (opcional, incluido por defecto)

## Carga en runtime

Con `REGATAS_LOAD_PROCESSED=1` (por defecto), `load_corpus_chunks()` concatena:

1. JSONL de esta carpeta
2. PDFs Call Book + Case Book (`corpus/*.pdf`)

Para reproducir solo el baseline (sin RRS indexado):

```bash
REGATAS_LOAD_PROCESSED=0 python scripts/eval_run.py ...
```

O eliminar temporalmente los `.jsonl` de esta carpeta.

## Identificadores de chunk

- RRS: `rrs|{numero_regla}` (ej. `rrs|16.1`); si hay varias filas CSV con el mismo número, `rrs|16.1#1`, …
- Definición: `definition|{id}`
- PDF: `{archivo}|p{página}|#{índice}` (sin cambios)
