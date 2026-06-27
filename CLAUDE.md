# 🦁 Samson Vision — CLAUDE.md

## Identity
Eres un asistente AI trabajando en **Samson Vision** — revelar el plan oculto bajo los píxeles. Un lenguaje visual textual (SVP) que permite a IAs sin visión "ver" imágenes y recuperar la visión del proyecto aunque el modelo siga siendo el mismo.

## Project structure
```
samson-vision/
├── src/                          # Código fuente
│   ├── samson_core.py            # Motor ASCII (8 estilos)
│   ├── samson_vision.py          # Generador SVP (13 campos)
│   ├── vmk/                      # Vision Multimodal Kernel
│   │   ├── kernel.py             # Color, bordes, saliency
│   │   └── scene_graph.py        # Bounding boxes, relaciones
│   ├── device_db.py              # 13 perfiles de dispositivo
│   ├── synesthesia.py            # Audio → ASCII
│   ├── harnesses.py              # Conectores de integración
│   └── versiculos.py             # Versículos decorativos (stderr)
├── test/
│   ├── run_tests.py              # 29 tests unitarios
│   └── test_integration.py       # 62 tests de integración
├── PUBLIC/                       # Documentación pública (GitHub)
│   ├── README.md                 # Landing (EN)
│   ├── INDEX.md                  # Navegación
│   └── docs/                     # Docs detallados
├── assets/                       # Imágenes de ejemplo (20 PNGs)
├── runtime/                      # RAG + validación + subagentes
├── setup.sh                      # Instalación automática
├── pyproject.toml                # Paquete Python instalable
└── requirements.txt
```

## Quick start
```bash
source .venv/bin/activate
python3 src/samson_vision.py assets/samson_pillars_crumbling.png --md
python3 test/run_tests.py
python3 test/test_integration.py
```

## SAMSON_VISION_PACK (SVP)
The core format: 13 fields → IMAGE_TYPE, GLOBAL_SUMMARY, VISUAL_HIERARCHY, LAYOUT_MAP, OCR_TEXT, OBJECTS_AND_COMPONENTS, COLOR_MAP, DENSITY_MAP, ASCII_REPRESENTATION, USER_ACTIONS, UNCERTAINTIES, DO_NOT_ASSUME, FINAL_INTERPRETATION.

## Key rules
- Pipeline is 100% algorithmic (numpy + OpenCV + Tesseract) — zero AI calls in generation.
- SVP interpretation can use any text-only LLM.
- Biblical metaphor: Samson (Judges 16:28-30) — revealing the plan hidden under pixels; agents recover project vision without switching to vision models.
- Output always goes to stdout; stderr for decoration (verse).
- Coordinates normalized 0-100.

## Dependencies
- Core: pillow, numpy
- Optional: opencv-python-headless, pytesseract
- Venv at .venv/

## Tests
- Unit: `python3 test/run_tests.py` — 29/29
- Integration: `python3 test/test_integration.py` — 59/59

## GitHub
- Private repo. PUBLIC/ is the sanitized public subset for future public release.
- assets/ are the canonical images (PUBLIC/assets/ was removed to avoid duplication).
Curated SVP demo images: see assets/README.md (2026-06-27: genesis_tablet_golden, lion_of_judah_revelation, +4 epic scenes).
