# 📖 SETUP — Instalación de Samson Vision

> Actualizado: 24-Jun-2026 | Verificado: 29/29 tests + SVP funcional

## Requisitos

- **Sistema:** Linux (probado Ubuntu 24.04), macOS o Windows
- **Python:** 3.10+
- **Dependencias:** pillow, numpy
- **Tesseract 5+** (opcional — OCR mejora extracción de texto)
- **OpenCV** (opcional — mejora detección de bordes y objetos)

## Instalación

### 1. Clonar o copiar el proyecto

```bash
# Si tienes acceso al repo:
git clone <repo-url> samson-vision
cd samson-vision

# Si ya tienes el proyecto local:
cd ~/proyectos/samson-vision   # ← ruta típica
```

### 2. Setup automático (recomendado)

```bash
bash setup.sh
```

Esto hace todo en un paso: crea venv, instala deps, instala el paquete, copia assets, ejecuta tests.

### 3. Setup manual (si prefieres paso a paso)

```bash
# Crear venv
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install pillow numpy

# Instalar el paquete en modo editable
pip install -e .

# Crear directorios de trabajo
mkdir -p input output

# Las imágenes de ejemplo están en assets/ (ya incluidas en el repo)
```

✅ **29/29 tests pasando**

## Tesseract OCR (opcional)

Tesseract mejora la precisión del campo OCR_TEXT en el SVP. Sin él, el pipeline funciona pero no extrae texto real.

**Linux (apt, requiere sudo):**
```bash
sudo apt install tesseract-ocr tesseract-ocr-spa tesseract-ocr-eng
```

**macOS (brew):**
```bash
brew install tesseract
```

**Windows:**
Descargar desde [GitHub tesseract-ocr/tesseract](https://github.com/tesseract-ocr/tesseract)

> **Sin sudo disponible:** Si no tienes permisos sudo, puedes:
> 1. Instalar Tesseract desde fuente en tu home: `./configure --prefix=$HOME/local && make && make install`
> 2. Usar conda: `conda install -c conda-forge tesseract`
> 3. O simplemente omitirlo — el pipeline sigue funcionando sin OCR

## Uso básico

### Generar un SVP desde una imagen

El proyecto incluye imágenes de ejemplo en `assets/`:

```bash
# Activar venv (si no lo está)
source .venv/bin/activate

# Generar SVP en Markdown desde assets/
samson-vision assets/samson_pillars_crumbling.png --md

# O directamente con python
python3 src/samson_vision.py assets/samson_pillars_crumbling.png --md

# Generar SVP en JSON
samson-vision assets/samson_pillars_crumbling.png --json
```

Cada ejecución imprime:
- **Stderr:** Un versículo decorativo (marca espiritual, no interfiere con la salida)
- **Stdout:** El SAMSON_VISION_PACK completo

### Redirigir a archivo

```bash
samson-vision assets/samson_pillars_crumbling.png --json > sample.svp.json
samson-vision assets/samson_pillars_crumbling.png --md > sample.svp.md

# O con python directo:
python3 src/samson_vision.py imagen.png --md 2>/dev/null
```

## Integración con Hermes Agent

Samson Vision está disponible como skill de Hermes:

```bash
# Cargar el skill y analizar una imagen
hermes -s samson-vision chat -q "Analiza esta imagen: /ruta/imagen.jpg"
```

El skill proporciona 3 modos de interpretación:
- **Fast** → MiniMax-M2.1 (mmx CLI) — 5s, más rápido
- **Balanced** → minimax-m2.5 (OpenCode) — 11s, más barato
- **Precise** → kimi-k2.7-code (OpenCode) — 8s, máxima precisión

## Interpretar el SVP con un LLM

El SVP es texto puro — puedes pasarlo a cualquier modelo de lenguaje:

### MiniMax M2.1 (vía mmx CLI) — 🏆 recomendado
```bash
SVP=$(python3 src/samson_vision.py imagen.png --md 2>/dev/null)
echo "$SVP" | mmx text chat --model MiniMax-M2.1 \
  --system "Interpreta este SAMSON_VISION_PACK como si vieras la imagen." \
  --message "$SVP" --temp 0.3
```

### OpenCode Go (minimax-m2.5)
```bash
SVP=$(python3 src/samson_vision.py imagen.png --md 2>/dev/null)
curl -s https://opencode.ai/zen/go/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENCCODE_API_KEY" \
  -d "{\"model\":\"minimax-m2.5\", \"messages\":[{\"role\":\"system\",\"content\":\"Interpreta este SAMSON_VISION_PACK.\"},{\"role\":\"user\",\"content\":\"$SVP\"}]}"
```

### Codex CLI (ChatGPT Plus)
```bash
SVP=$(python3 src/samson_vision.py imagen.png --md 2>/dev/null)
codex -z "Eres Samson Vision. Interpreta este SAMSON_VISION_PACK: $SVP"
```

## Harness de fallback

El orden recomendado para interpretar SVP:

```
PASO 1: MiniMax-M2.1 (mmx CLI)       → 5s   → $0.0008/query → 100% calidad
PASO 2: minimax-m2.5 (OpenCode Go)    → 11s  → $0.0009/query → 83% calidad
PASO 3: kimi-k2.7-code (OpenCode Go)  → 8s   → $0.003/query  → 100% calidad
PASO 4: gpt-5.4-mini (Codex CLI)      → 8s   → $20/mes fijo  → 100% calidad
```

**Modelos que NO funcionan con SVP:** deepseek-v4-flash, deepseek-v4-pro, GLM-5.x, qwen3.7-max, kimi-k2.6/k2.5

## Arquitectura del proyecto

```
samson-vision/
├── src/
│   ├── samson_core.py           → 8 estilos ASCII + metadatos
│   ├── samson_vision.py         → SAMSON_VISION_PACK (13 campos)
│   ├── versiculos.py            → Versículos decorativos (stderr)
│   ├── device_db.py             → 13 perfiles de dispositivo
│   ├── synesthesia.py           → Audio → ASCII
│   ├── harnesses.py             → Arneses Hermes/M3/Codex
│   ├── runtime_integration.py   → Conexión runtime RAG
│   └── vmk/                     → Vision Multimodal Kernel
├── test/run_tests.py            → 29 tests
├── runtime/                     → RAG + validación + subagentes
├── assets/                      → 20 imágenes de ejemplo
├── input/                       → Tus imágenes para analizar
├── output/                      → SVP generados
├── setup.sh                     → Instalación automática
├── pyproject.toml               → Paquete Python instalable
├── requirements.txt             → Dependencias
├── PUBLIC/                      → Documentación pública
│   ├── README.md
│   └── docs/                    → ARCHITECTURE, BENCHMARK, COSTS, SETUP, SAMSON_VISION_PACK
└── README.md                    → Proyecto completo
```

## Solución de problemas

| Problema | Solución |
|----------|----------|
| `ModuleNotFoundError: PIL` | `pip install pillow` |
| `ModuleNotFoundError: numpy` | `pip install numpy` |
| `ModuleNotFoundError: cv2` | `pip install opencv-python-headless` (opcional) |
| `from samson_core import __version__` falla | ¿Ejecutaste `pip install -e .`? El paquete debe estar instalado |
| `samson-vision: command not found` | Activa el venv: `source .venv/bin/activate` |
| OCR muestra `[text_zone]` | Sin Tesseract — instálalo o ignóralo |
| `hermes -s samson-vision` no funciona | El skill debe estar instalado en Hermes |
| El SVP tiene header pero campos vacíos | La imagen no tiene contenido procesable — prueba con una imagen más rica |

## Notas importantes

- Los versículos se imprimen a **stderr** — nunca contaminan stdout. Usa `2>/dev/null` para silenciarlos
- Sin Tesseract: el OCR salta gracefulmente, el pipeline sigue funcionando al 100%
- Sin OpenCV: la detección de objetos usa PIL básico, menos preciso
- El banner `[SAMSON_VISION_PACK v1]` con versículo confirma que el pipeline está operativo
- **No hay servidor HTTP.** Samson Vision se usa por CLI o integrado via Hermes skill
