# 🦁 Samson Vision — Arquitectura técnica

> **Pipeline imagen → texto estructurado (SVP) para que cualquier LLM de texto "vea" imágenes.**
> Zero AI dependency en el pipeline — solo numpy + OpenCV + Tesseract.

## Visión general

## Why Samson Vision?

Sansón perdió la **vista física**, pero recuperó la **visión del plan de Dios** (Jueces 16:28-30). En su debilidad, Dios le dio visión para actuar en el momento justo (Jueces 16:28-30). Samson Vision aplica la misma idea a agentes de IA: tu modelo **sigue sin ojos** (sin modelo de visión), pero recibe **visión** a través del SVP — 13 campos de texto que codifican la verdad estructural que los píxeles esconden. Los modelos con visión nativa son caros, a menudo más débiles en código y razonamiento, y cambiar de agente borra el contexto. SVP permite que cualquier LLM de texto "vea" sin cambiar de modelo ni pagar APIs de visión.

*Samson lost physical sight but gained vision of God's plan. The AI still has no eyes — Samson Vision gives it sight through SVP text anyway.*


Samson Vision es un **pipeline algorítmico** que transforma cualquier imagen en un **SAMSON_VISION_PACK (SVP)**: 13 campos de texto estructurado que cualquier modelo de lenguaje puede interpretar como si estuviera viendo la imagen.

```
Imagen (PNG/JPG/WEBP) 
        ↓
  ┌─ samson_core.py ──────────────────┐
  │  8 estilos ASCII (standard,       │
  │  detail, block, edge, color,      │
  │  dither, fanart, braille)         │
  └────────────────┬──────────────────┘
                   ↓
  ┌─ vmk/ (Vision Multimodal Kernel) ─┐
  │  kernel.py: color, bordes,        │
  │  saliency, detección de objetos   │
  │  scene_graph.py: BBox, relaciones │
  └────────────────┬──────────────────┘
                   ↓
  ┌─ samson_vision.py ────────────────┐
  │  Ensambla los 13 campos del SVP   │
  │  Header + OCR + layout + ASCII +  │
  │  antialucinación + interpretación │
  └────────────────┬──────────────────┘
                   ↓
        [SAMSON_VISION_PACK v1] (texto)
                   ↓
         ┌─ Any LLM de texto ─┐
         │  interpreta el SVP  │
         │  como si "viera"    │
         └─────────────────────┘
```

## Flujo con subagentes (orquestación multi-agente)

Samson Vision encaja en arquitecturas donde un **agente principal** delega trabajo a **subagentes** especializados. Los subagentes suelen ser modelos **solo texto** (más baratos, más capaces en código) pero **sin visión nativa**.

```
┌─────────────────┐     imagen/screenshot
│  Agente         │──────────────────────────────┐
│  principal      │                              │
└────────┬────────┘                              ▼
         │                          ┌────────────────────────┐
         │                          │  samson_vision.py      │
         │                          │  --md → SVP (13 campos)│
         │                          └───────────┬────────────┘
         │                                      │ texto estructurado
         │  prompt + SVP embebido               │
         ▼                                      ▼
┌─────────────────┐                    ┌─────────────────┐
│  Subagente      │◄───────────────────│  Contexto:      │
│  (texto, sin    │   "visión" en SVP  │  tarea + SVP    │
│   visión)       │                    └─────────────────┘
└────────┬────────┘
         │ resultado
         ▼
┌─────────────────┐
│  Agente         │ → síntesis / entrega al usuario
│  principal      │
└─────────────────┘
```

**Ventajas del patrón:**

| Aspecto | Sin SVP | Con SVP + subagente |
|---------|---------|---------------------|
| Modelo del subagente | Requiere visión nativa (caro) | Solo texto (barato) |
| Contexto visual | Se pierde al cambiar modelo | SVP portable en texto |
| Coste por delegación | API de visión por imagen | ~$0 generación + interpretación texto |
| Habilidades del subagente | Se degradan con modelos multimodales | Se mantienen intactas |

Los contratos de subagente en `runtime/subagents/` pueden incluir el SVP como bloque obligatorio cuando la tarea incluye input visual.

*Main agent generates SVP; text-only subagent receives embedded structured vision — no vision API on the subagent.*


## Componentes

### 1. samson_core.py — Motor de conversión ASCII

Transforma píxeles a arte ASCII con **8 estilos**:

| Estilo | Caracteres | Uso |
|--------|-----------|-----|
| **standard** | `@%#*+=-:. ` (10 niv.) | Vista rápida, texto plano |
| **detail** | `@%#&WM...` (28 niv.) | Precisión, documentos |
| **block** | `██▄▀ ░▒▓` (Unicode) | Dark mode, alto contraste |
| **edge** | Bordes Canny + ASCII | Estructura, diagramas |
| **color** | ANSI escape + caracteres | Comprensión cromática |
| **dither** | Floyd-Steinberg | Fotos, degradados |
| **fanart** | Patrones invertidos | Creativo |
| **braille** | Unicode Braille (⣿⣧⣄) | Compresión extrema |

**Input:** PIL Image, width/height opcional (default 80×40)
**Output:** Diccionario con 8 representaciones + metadatos (brillo medio, contraste)

### 2. vmk/ — Vision Multimodal Kernel

Dos módulos:

**kernel.py** — Análisis multi-capa de la imagen:
- `process_image(img)` → color promedio, brillo, contraste, bordes, saliency
- `get_last_scene_graph()` → grafo completo de la escena
- `get_last_objects()` → bounding boxes de objetos detectados

**scene_graph.py** — Estructura de escena:
- `SceneGraph`: contenedor con nodos, relaciones y metadatos
- `SceneNode(cx, cy, width, height, label, confidence, level)`: elemento individual con bounding box normalizado (0-100)
- `BBoxHelper`: utilidades de coordenadas y solapamiento
- Soporta proximidad, contención, alineación y superposición

### 3. samson_vision.py — Generador del SAMSON_VISION_PACK

Ensambla el SVP combinando salidas de Core + VMK + OCR + metadatos:

```
[SAMSON_VISION_PACK v1]

IMAGE_TYPE:           dominio, dimensión, calidad
GLOBAL_SUMMARY:       resumen visual (1-2 oraciones)
VISUAL_HIERARCHY:     elementos ordenados por importancia
LAYOUT_MAP:           zonas con coordenadas normalizadas (0-100)
OCR_TEXT:             texto detectado (Tesseract) con confianza
OBJECTS_AND_COMPONENTS: objetos con bounding boxes
COLOR_MAP:            paleta dominante con nombres textuales
DENSITY_MAP:          densidad visual por franjas (alta/media/baja)
ASCII_REPRESENTATION: mapa ASCII multi-estilo
USER_ACTIONS:         puntos de interacción con coordenadas
UNCERTAINTIES:        límites explícitos de detección
DO_NOT_ASSUME:        guardas antialucinación
FINAL_INTERPRETATION: síntesis para IA de texto puro
```

**OCR:** Tesseract con preprocesado (escalado 2x + OTSU + agrupación por líneas). Sin Tesseract → salta gracefulmente.

**Dos formatos de salida:**
- `--md` → Markdown estructurado (humano + LLM)
- `--json` → JSON (procesamiento programático)

### 4. device_db.py — Base de dispositivos

SQLite con 13 perfiles de dispositivo (iPhone SE, iPad Pro, 4K monitor, etc.) para testing responsive. Cada perfil: nombre, resolución, DPI, tipo.

### 5. synesthesia.py — Audio → visualización ASCII

Convierte audio (WAV) a: ASCII waveform, espectro de frecuencias, patrón de beats.

### 6. harnesses.py — Arneses de integración

Conectores para usar Samson Vision con modelos externos:
- **Hermes Agent** vía perfil `vision` + skill `samson-vision`
- **MiniMax M3** vía `mmx vision describe`
- **Codex CLI** para debugging
- **Pipeline completo** (SV + VMK + M3 + Codex)

### 7. runtime/ — Sistema RAG completo

Conocimiento de dominio para generar SVP más precisos:
- **knowledge/:** 16 archivos (reglas, patrones web/Excel/dashboard, léxico de colores, antialucinación, validación)
- **rag_index.jsonl:** 27 entradas indexadas
- **scripts/:** runtime, validador, demo, smoke test
- **subagents/:** 7 contratos para orquestación multi-agente

## Pipeline de datos

```
┌──────────────┐     ┌──────────────────┐     ┌──────────────────────┐
│   Imagen     │────→│   samson_core    │────→│  8 estilos ASCII     │
│              │     │                  │     │  + metadatos básicos │
└──────────────┘     └──────────────────┘     └──────────────────────┘
                            │                           │
                            ↓                           │
                    ┌──────────────────┐                │
                    │   vmk/kernel     │                │
                    │  (color, bordes, │                │
                    │   saliency, obj) │                │
                    └────────┬─────────┘                │
                             │                          │
                             ↓                          │
                    ┌──────────────────┐                │
                    │ vmk/scene_graph  │                │
                    │ (BBox, objeto,   │                │
                    │  relaciones)     │                │
                    └────────┬─────────┘                │
                             │                          │
                             ↓                          ↓
                    ┌──────────────────────────────────────┐
                    │        samson_vision.py               │
                    │   Ensambla SVP: 13 campos             │
                    │   ASCII + coordenadas + OCR + colores │
                    │   + jerarquía + antialucinación       │
                    └──────────────────┬───────────────────┘
                                       ↓
                    ┌──────────────────────────────────────┐
                    │     [SAMSON_VISION_PACK v1]           │
                    │     Texto estructurado (MD o JSON)    │
                    └──────────────────┬───────────────────┘
                                       ↓
                    ┌──────────────────────────────────────┐
                    │     Cualquier LLM de texto            │
                    │     (MiniMax, Codex, Kimi, etc.)      │
                    └──────────────────────────────────────┘
```

## Sin dependencia de IA

El pipeline **completo** de generación del SVP es **0% IA**:

| Componente | Tecnología | Coste |
|-----------|-----------|:-----:|
| ASCII conversion | numpy + PIL | $0 |
| Detección de bordes | OpenCV Canny | $0 |
| Saliency | OpenCV saliency | $0 |
| OCR | Tesseract (preprocesado) | $0 |
| Paleta de colores | numpy clustering | $0 |
| Scene graph | Algoritmos propios | $0 |
| Validación SVP | Reglas en Python | $0 |

Solo la **interpretación** del SVP (pasarlo a un LLM) tiene coste de API.

## Stack recomendado (80/20)

```
🏆 Primario:   MiniMax-M2.1 (mmx CLI)    → 5s,   $0.0008/q, 100%
🔄 Fallback:   minimax-m2.5 (OpenCode)    → 11s,  $0.0009/q, 83%
🎯 Precisión:  kimi-k2.7-code (OpenCode)  → 8s,   $0.003/q,  100%
🎫 Backup:     GPT-5.4-mini (Codex CLI)   → 8s,   ~$0.0005/q ($0.15/$0.60 per 1M in/out est.)
```

**Modelos que NO funcionan:** deepseek flash v4, GLM-5.x, kimi-k2.6/k2.5, qwen3.7-max

## Almacenamiento del proyecto

```
~/proyectos/samson-vision/
├── src/                        ← Código fuente
│   ├── samson_core.py          → Motor ASCII (8 estilos)
│   ├── samson_vision.py        → SVP generator (13 campos)
│   ├── versiculos.py           → Versículos decorativos (stderr)
│   ├── device_db.py            → 13 perfiles de dispositivo
│   ├── synesthesia.py          → Audio → ASCII
│   ├── harnesses.py            → Arneses Hermes/M3/Codex
│   ├── runtime_integration.py  → Conexión con runtime RAG
│   └── vmk/                    → Vision Multimodal Kernel
│       ├── kernel.py           → Orquestador multi-capa
│       └── scene_graph.py      → Scene graph con BBox
├── test/run_tests.py           → 29 tests unitarios
├── runtime/                    → RAG + validación + subagentes
│   ├── knowledge/              → 16 archivos de conocimiento
│   ├── scripts/                → Runtime CLI + validador
│   ├── subagents/              → 7 contratos de subagentes
│   ├── harness/                → Harness prompts
│   └── examples/               → Ejemplos buenos/malos
├── PUBLIC/                     → Documentación sanitizada
│   ├── README.md               → Landing público
│   ├── INDEX.md                → Navegación
│   ├── assets/                 → 20 imágenes representativas
│   └── docs/                   → Documentación completa
└── README.md                   → Este archivo
```

## La metáfora de Sansón

> Sansón perdió la **vista física**, pero recuperó la **visión del plan de Dios** (Jueces 16:28-30).
>
> En su debilidad, Dios le dio visión para actuar en el momento justo (Jueces 16:28-30).
>
> **Samson Vision** — *tus limitaciones no son un límite imposible de superar* (Filipenses 4:13). Tu agente **sigue sin ojos** — el mismo modelo, sin visión — pero recibe **visión** a través del SVP: la verdad estructural que los píxeles esconden y que un LLM ciego no puede captar solo.
>
> *The AI still has no eyes — no vision model — but Samson Vision gives it sight anyway through SVP text.*
