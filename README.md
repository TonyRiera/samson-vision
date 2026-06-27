<p align="center">
  <img src="assets/final_moment_pillars.png" width="720" alt="Samson Vision — el momento final entre los pilares">
</p>

<h1 align="center">Samson Vision</h1>

<p align="center">
  <em>ES:</em> Tus limitaciones no son un límite imposible de superar. <em>Filipenses 4:13</em>
</p>
<p align="center">
  <em>EN:</em> Your limitations are not an impossible limit to overcome. <em>Philippians 4:13</em>
</p>
<p align="center">
  Tu agente sigue sin ojos — el mismo modelo, sin visión — pero recibe visión a través del SVP.
</p>
<p align="center">
  <em>Your agent still has no eyes — same model, no vision — but receives sight through SVP.</em>
</p>


<p align="center">
  <a href="PUBLIC/docs/SETUP.md"><strong>Instalar</strong></a>
  &nbsp;·&nbsp;
  <a href="#uso-rápido"><strong>Inicio rápido</strong></a>
  &nbsp;·&nbsp;
  <a href="index.html"><strong>Landing</strong></a>
  &nbsp;·&nbsp;
  <a href="PUBLIC/docs/SAMSON_VISION_PACK.md"><strong>SVP</strong></a>
</p>

Sansón pudo ver aun sin ojos. Tu agente recuperará la **visión del proyecto** aunque su modelo siga siendo el mismo — sin modelos con visión que encarecen y pierden habilidades.

**El problema:** Los agentes limitados por APIs de visión pierden errores estructurales, cambiar de modelo borra el contexto, y los modelos multimodales cuestan más mientras sacrifican profundidad en código y razonamiento.

**La respuesta:** El **SAMSON_VISION_PACK (SVP)** — 13 campos de texto estructurado que reemplazan la necesidad de enviar imágenes a LLMs costosos. Mismo modelo. Mismas habilidades. Comprensión visual completa a través de texto.

*This project is shared as a personal blessing — so teams are not forced into expensive vision models when text-only agents can see just as clearly through SVP.*


---

## ¿Qué es?

Samson Vision es un **lenguaje visual basado en texto** que permite a una IA sin visión "ver" imágenes. Traduce píxeles al **SAMSON_VISION_PACK (SVP)** — un formato estructurado con 13 campos — que cualquier modelo de texto puede interpretar como si estuviera viendo la imagen.

## Flujo con subagentes / Subagent workflow

Flujo real de orquestación (validado en `runtime/NOUS_AGENT_BLUEPRINT.md` y contratos en `runtime/subagents/`). Jordan pendiente de confirmar detalles operativos en claw.

| Rol | Modelo típico | Visión nativa | Función |
|-----|---------------|:-------------:|---------|
| **Agente principal** (orquestador) | **DeepSeek Flash v4** | ❌ No | Coordina, lee SVP, delega, sintetiza |
| **Subagente de visión** | vision_scout / multimodal | ✅ Sí | Analiza la imagen, refina o valida el pack |
| **Samson Vision CLI** | Pipeline algorítmico | — | Genera SVP (0% IA, numpy+OpenCV+Tesseract) |

**Quién ejecuta el CLI y cuándo:** el **agente principal o su harness** (Jordan/Hermes, Cursor orchestrator) invoca `samson-vision imagen.png --md` **antes de delegar**, en cuanto la tarea incluye imagen o screenshot. El subagente con visión **no** sustituye al CLI — recibe además la imagen nativa.

**Rol del SVP en la delegación:**
1. El orquestador **sin visión** lee el SVP como texto estructurado (13 campos) para entender la escena.
2. Embebe el SVP en el prompt de delegación junto con la ruta/archivo de imagen.
3. El **subagente con visión** trabaja con imagen + contexto SVP (layout, OCR, coordenadas).
4. El resultado vuelve al orquestador DeepSeek Flash v4 para síntesis o entrega.

> **Nota benchmark:** DeepSeek Flash v4 como **orquestador** lee SVP en contexto. Como **intérprete SVP vía API** (modo text_reasoner) devuelve vacío — usar MiniMax/kimi para interpretación LLM del pack.

```mermaid
sequenceDiagram
    participant U as Usuario / Tarea
    participant M as Agente principal<br/>(DeepSeek Flash v4, sin visión)
    participant SV as Samson Vision CLI
    participant V as Subagente con visión<br/>(vision_scout)

    U->>M: Tarea + imagen/screenshot
    M->>SV: samson-vision imagen.png --md
    Note over SV: Pipeline 0% IA<br/>numpy + OpenCV + Tesseract
    SV-->>M: SVP (13 campos)
    M->>M: Lee SVP → planifica delegación
    M->>V: prompt + imagen + SVP embebido
    Note over V: Visión nativa incorporada
    V-->>M: Análisis / borrador pack / acciones
    M-->>U: Respuesta integrada
```

**Pasos:**

1. El **agente principal** (DeepSeek Flash v4, sin visión) recibe tarea con imagen.
2. **Antes de delegar**, ejecuta Samson Vision CLI → SVP (`samson-vision imagen.png --md` o `python3 src/samson_vision.py …`).
3. Lee el SVP para orientarse (layout, OCR, jerarquía) sin API de visión.
4. **Delega al subagente con visión**: prompt + imagen + SVP en contexto.
5. El subagente (`vision_scout` en `runtime/subagents/`) analiza con visión nativa.
6. El **resultado vuelve al orquestador** para validación, corrección o entrega.

*Main agent (DeepSeek Flash v4, no vision) runs Samson CLI first, reads SVP, then delegates to a vision-capable subagent with image + embedded SVP.*

## Casos de uso / Use cases

Patrón común: **agente principal sin visión** (p. ej. DeepSeek Flash v4) + **Samson SVP** (el principal **ve en texto antes de delegar**) + **subagente con visión incorporada** — sin multimodal caro en el orquestador ni pérdida de habilidades de código.

*Common pattern: **visionless main agent** (e.g. DeepSeek Flash v4) + **Samson SVP** (sight for the principal before delegation) + **subagent with built-in vision** — no expensive vision on the orchestrator, no loss of coding depth.*

- **Orquestador barato revisa screenshot de UI** · *Cheap orchestrator reviews UI screenshot*
  - **ES:** El agente principal (sin visión) genera el SVP del screenshot de regresión, **lee el pack en texto**, entiende el fallo y delega al subagente (con visión incorporada) el fix CSS/layout — el orquestador no usa API multimodal.
  - **EN:** Visionless main agent builds SVP from the regression screenshot, **reads the pack as text**, understands the issue, and delegates CSS/layout fix to a vision-capable subagent — no multimodal API on the orchestrator.

- **CI/CD sin modelo de visión en orquestador** · *CI/CD without vision on orchestrator*
  - **ES:** El pipeline corre Samson CLI tras cada build. El orquestador (sin visión) compara SVPs (layout, OCR, colores) y detecta regresión en texto; los subagentes con visión validan casos dudosos sobre capturas reales — sin GPT-4V en el agente principal.
  - **EN:** Pipeline runs Samson CLI post-build; visionless orchestrator diffs SVPs; vision-enabled subagents confirm edge cases on real captures — no vision model on the main pipeline agent.

- **Subagente Cursor con visión** · *Cursor vision subagent*
  - **ES:** El orquestador (sin visión) **lee el SVP** para redactar una delegación precisa (Hermes, Cursor) y pasa la imagen. El subagente, con visión incorporada, ejecuta en el repo y valida UI con sus propios ojos.
  - **EN:** Visionless orchestrator **reads SVP** to craft precise delegation and passes the image; vision-capable subagent executes in-repo and validates UI natively.

- **Auditoría de accesibilidad** · *Accessibility audit*
  - **ES:** El agente principal (sin visión) prioriza hallazgos desde `OCR_TEXT`, `LAYOUT_MAP`, `COLOR_MAP` y `USER_ACTIONS` del SVP; delega al subagente con visión la remediación y comprobación visual — sin multimodal en el orquestador.
  - **EN:** Visionless main triages issues from SVP OCR, layout, color, and actions; vision-enabled subagent remediates and visually verifies — no vision model on the orchestrator.

- **Portfolio y evidencia de producción** · *Portfolio / production evidence*
  - **ES:** El principal (sin visión) lee SVP de capturas de prod para redactar case study o informe QA versionable; el subagente con visión valida fidelidad y detalle fino — sin API de visión en el orquestador.
  - **EN:** Visionless main reads prod SVPs for versionable case studies or QA reports; vision subagent validates fidelity and fine detail — no vision API on the orchestrator.

- **Multimodal caro evitado en orquestador** · *Expensive multimodal avoided on orchestrator*
  - **ES:** Orquestador barato (DeepSeek Flash v4) + SVP para **ver antes de delegar**; subagente con visión nativa para ejecución — frente a visión cara en todo el stack: ~100× menor coste en el principal, razonamiento intacto.
  - **EN:** Cheap visionless orchestrator + SVP for sight before delegation; native vision on subagent for execution — vs expensive vision everywhere: ~100× lower cost on the principal, reasoning preserved.



## Stack 80/20 — Modelo más rápido + fallback

```
SVP → MiniMax-M2.1 (mmx CLI)  → 5s, $0.0008/query, 100% calidad  ← 🏆 PRIMARIO
SVP → minimax-m2.5 (OpenCode) → 11s, $0.0009/query, 83% calidad   ← 🔄 FALLBACK
SVP → kimi-k2.7-code (OpenCode) → 8s, $0.003/query, 100% calidad   ← 🎯 PRECISIÓN
```

El flujo es automático: primero intenta M2.1 (5s). Si falla, cae a M2.5. Si necesitas máxima precisión, usa Kimi K2.7.

## Benchmark completo — 24 modelos testeados

Ver [`docs/COSTS.md`](docs/COSTS.md) para costes detallados.

| # | Modelo | Via | Calidad | Tiempo | Coste/query | Cobertura |
|---|--------|-----|:-----:|:------:|:----------:|:---------:|
| 1 | **MiniMax-M2.1** 🏆 | mmx CLI | 100% | **5s** | $0.0008 | ✅✅✅✅✅✅ |
| 2 | **kimi-k2.7-code** | OpenCode | 100% | 8s | $0.0030 | ✅✅✅✅✅✅ |
| 3 | gpt-5.4-mini | Codex | 100% | 8s | subscription (per-token) | ✅✅✅✅✅✅ |
| 4 | **minimax-m2.5** 🥈 | OpenCode | 83% | 11s | **$0.0009** | ✅✅✅✅✅❌ |
| 5 | MiniMax-M2.7-highspeed | mmx | 83% | 11s | $0.0016 | ✅✅✅✅✅❌ |
| 6 | minimax-m3 | OpenCode | 67% | 10s | $0.0009 | ✅✅✅❌❌✅ |
| 7 | mimo-v2-omni | OpenCode | 67% | 9s | $0.0029 | ✅✅✅❌❌✅ |
| 8 | qwen3.5-plus | OpenCode | 67% | 43s | $0.0012 | ✅✅✅❌❌❌ |
| ❌ | deepseek flash v4 | OpenCode | 0% | — | $0.0003 | vacío (0%) |
| ❌ | glm-5.2/5.1/5 | OpenCode | 0% | — | $0.0039 | vacío (0%) |

## El Lenguaje: SAMSON_VISION_PACK (SVP)

El SVP es un formato de 13 campos que traduce cualquier imagen a texto estructurado:

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
# Generar SVP de una imagen
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
| **SVP + modelo texto** | Cuando el modelo no ve imágenes | $0.0008-$0.003/query |
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
│   ├── SAMSON_VISION_PACK.md ← SVP spec (13 fields)
│   ├── BENCHMARK.md       ← Model comparison
│   ├── SETUP.md           ← Installation guide
│   └── COSTS.md           ← Usage costs
```

Contenido sanitizado: sin rutas personales (~/), sin API keys, sin detalles de cuentas,
sin nombres de usuario, sin configuraciones internas. Listo para copiar a un repo público.
