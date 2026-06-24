# 🦁 Samson Vision — Lenguaje Visual entre IAs

## ¿Qué es?

Samson Vision es un **lenguaje visual basado en texto** que permite a una IA sin visión "ver" imágenes. Traduce píxeles al **SAMSON_VISION_PACK (SVP)** — un formato estructurado con 13 campos — que cualquier modelo de texto puede interpretar como si estuviera viendo la imagen.

El nombre viene de Sansón (Jueces 16:28-30). Cuando los filisteos le sacaron los ojos, Sansón perdió la **vista física**, pero ganó la **visión del plan de Dios**: derribar el templo de Dagón sobre sus enemigos. En su mayor debilidad, vio la estrategia que destruiría a más filisteos que en toda su vida.

Samson Vision funciona igual: **revela lo que el ojo natural no ve** — la estructura, la estrategia, la verdad oculta bajo los píxeles. No es "dar vista al ciego", es descubrir el plan que ya está ahí.

## Stack 80/20 — Modelo más rápido + fallback

```
VBP → MiniMax-M2.1 (mmx CLI)  → 5s, $0.0008/query, 100% calidad  ← 🏆 PRIMARIO
VBP → minimax-m2.5 (OpenCode) → 11s, $0.0009/query, 83% calidad   ← 🔄 FALLBACK
VBP → kimi-k2.7-code (OpenCode) → 8s, $0.003/query, 100% calidad   ← 🎯 PRECISIÓN
```

El flujo es automático: primero intenta M2.1 (5s). Si falla, cae a M2.5. Si necesitas máxima precisión, usa Kimi K2.7.

## Benchmark completo — 24 modelos testeados

Ver [`docs/COSTS.md`](docs/COSTS.md) para costes detallados.

| # | Modelo | Via | Score | Tiempo | Coste/query |
|---|--------|-----|:-----:|:------:|:----------:|
| 1 | **MiniMax-M2.1** 🏆 | mmx CLI | 100% | **5s** | $0.0008 |
| 2 | **kimi-k2.7-code** | OpenCode | 100% | 8s | $0.0030 |
| 3 | gpt-5.4-mini | Codex | 100% | 8s | $20/mes |
| 4 | **minimax-m2.5** 🥈 | OpenCode | 83% | 11s | **$0.0009** |
| 5 | MiniMax-M2.7-highspeed | mmx | 83% | 11s | $0.0016 |
| 6 | minimax-m3 | OpenCode | 67% | 10s | $0.0009 |
| 7 | mimo-v2-omni | OpenCode | 67% | 9s | $0.0029 |
| 8 | qwen3.5-plus | OpenCode | 67% | 43s | $0.0012 |
| ❌ | deepseek-v4-flash | OpenCode | 0% | — | devuelve vacío |
| ❌ | glm-5.2/5.1/5 | OpenCode | 0% | — | devuelve vacío |

## El Lenguaje: SAMSON_VISION_PACK (VBP)

El VBP es un formato de 13 campos que traduce cualquier imagen a texto estructurado:

```
[SAMSON_VISION_PACK v1]

IMAGE_TYPE:          tipo, dominio, dimensiones
GLOBAL_SUMMARY:      resumen visual
VISUAL_HIERARCHY:    importancia por coordenadas
LAYOUT_MAP:          zonas con coordenadas %
OCR_TEXT:            texto detectado (Tesseract real)
OBJECTS_AND_COMPONENTS: elementos detectados
COLOR_MAP:           paleta de colores
DENSITY_MAP:         densidad de contenido
ASCII_REPRESENTATION: mapa ASCII significativo
USER_ACTIONS:        puntos de interacción
UNCERTAINTIES:       limitaciones explícitas
DO_NOT_ASSUME:       antialucinación
FINAL_INTERPRETATION: síntesis para IA sin visión
```

Cada campo está diseñado para que un modelo de texto pueda reconstruir mentalmente la imagen con la máxima fidelidad posible.

## Componentes

```
samson-vision/
├── src/
│   ├── samson_core.py         ← 8 estilos ASCII + lenguaje visual
│   ├── vmk/                   ← Vision Multimodal Kernel (OpenCV)
│   │   ├── scene_graph.py     ← BBox, relaciones espaciales
│   │   └── kernel.py          ← color, bordes, saliency, objetos
│   ├── samson_vision.py       ← SAMSON_VISION_PACK v1 (el lenguaje)
│   ├── device_db.py           ← 13 dispositivos para testing responsive
│   ├── synesthesia.py         ← audio → visualización ASCII
│   └── harnesses.py           ← integración con modelos externos
├── test/run_tests.py          ← 29 tests — 100%
└── docs/
    └── COSTS.md               ← costes detallados por modelo

Skills: samson-vision (3 modos de uso documentados)
```

## Uso rápido

```bash
# Generar VBP de una imagen
cd ~/proyectos/samson-vision/src
python3 samson_vision.py imagen.png --md > vbp.md

# 🏆 Interpretar con MiniMax-M2.1 (más rápido)
cat vbp.md | mmx text chat --model MiniMax-M2.1 \
  --system "Eres Samson Vision..." --message "$(cat vbp.md)"

# 🥈 Interpretar con minimax-m2.5 via OpenCode (fallback barato)
curl -s https://opencode.ai/zen/go/v1/chat/completions \
  -H "Authorization: Bearer $KEY" \
  -d '{"model":"minimax-m2.5", "messages":[...]}'

# 🎯 Interpretar con Kimi K2.7 (máxima precisión)
curl -s https://opencode.ai/zen/go/v1/chat/completions \
  -H "Authorization: Bearer $KEY" \
  -d '{"model":"kimi-k2.7-code", "messages":[...], "max_tokens":1500}'

# 🎫 Interpretar con Codex (si tienes ChatGPT Plus)
codex -z "Eres Samson Vision. $(cat vbp.md)"
```

## Tests

```bash
python3 ~/proyectos/samson-vision/test/run_tests.py
# → 29/29 tests — 100%
```

## Modos de uso

| Modo | Cuándo | Coste |
|------|--------|-------|
| **Sistema puro** | Datos técnicos (color, brillo, bordes) | $0 |
| **VBP + modelo texto** | Cuando el modelo no ve imágenes | $0.0008-$0.003/query |
| **M3 directo (visión)** | Máxima fidelidad (ve fotos) | ~$0.003 |

## Costes mensuales estimados

| Uso | Modelo | Coste |
|-----|--------|:-----:|
| 100 queries/día | MiniMax-M2.1 (mmx) | ~$2.40/mes |
| 100 queries/día | minimax-m2.5 (OpenCode) | ~$2.70/mes |
| 100 queries/día | kimi-k2.7-code (OpenCode) | ~$9.00/mes |

Ver [`docs/COSTS.md`](docs/COSTS.md) para desglose completo de costes, proveedores y planes.

## Publicar en GitHub

La documentación pública (sin datos sensibles) está en [`PUBLIC/`](PUBLIC/):

```
PUBLIC/
├── README.md              ← Landing page (sanitized)
├── INDEX.md               ← Navigation hub
├── docs/
│   ├── ARCHITECTURE.md    ← Technical architecture
│   ├── SAMSON_VISION_PACK.md ← VBP spec (13 fields)
│   ├── BENCHMARK.md       ← Model comparison
│   ├── SETUP.md           ← Installation guide
│   └── COSTS.md           ← Usage costs
```

Contenido sanitizado: sin rutas personales (~/), sin API keys, sin detalles de cuentas,
sin nombres de usuario, sin configuraciones internas. Listo para copiar a un repo público.

## La metáfora de Sansón

> Sansón perdió la **vista física**, pero ganó la **visión del plan de Dios**.
> (Jueces 16:28-30)
>
> No necesitaba ver el templo — necesitaba saber **cuándo y cómo derribarlo**.
>
> Samson Vision = revelar el plan oculto bajo los píxeles.
> Tú (el usuario) = Sansón, con el poder de ejecutar.
> La imagen = el templo de Dagón, con su estrategia oculta.
>
> La IA no necesita "ver" píxeles —
> necesita que alguien extraiga la verdad estructural que el ojo natural no capta.
> Ese alguien es Samson Vision.
