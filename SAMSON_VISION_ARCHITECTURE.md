# 🦁 Samson Vision → Samson Vision: Análisis Arquitectónico Completo

**Fecha:** 2025-06-23
**Estado:** v2.0 actual → v3.0 propuesto
**Autor:** Análisis arquitectónico independiente

---

## 1. DIAGNÓSTICO DEL ESTADO ACTUAL

### Lo que funciona bien (no tocar)
| Componente | Líneas | Valor | Veredicto |
|---|---|---|---|
| samson_core.py (8 estilos) | 407 | ⭐⭐⭐⭐⭐ | Excelente. Los 8 estilos están bien diseñados. |
| vmk/kernel.py (análisis) | ~350 | ⭐⭐⭐⭐ | Bueno. Análisis de color/bordes/saliency sólido. |
| vmk/scene_graph.py | ~160 | ⭐⭐⭐⭐ | Correcto. BBox, relaciones espaciales, serialización. |
| synesthesia.py | 576 | ⭐⭐⭐ | Funcional pero no core para Samson Vision. |
| device_db.py | 468 | ⭐⭐ | Útil para responsive testing, no crítico para VB. |
| harnesses.py | 291 | ⭐⭐⭐ | Patrón correcto pero depende de externos. |

### Deuda técnica detectada
1. **scene_graph.py** — `infer_spatial_relations()` crea edges duplicados (LEFT + NEAR + OVERLAPS para el mismo par)
2. **kernel.py** — `detect_objects_simple()` es O(n²) para fusionar regiones (merge cuadrático)
3. **samson_core.py** — `_ascii_from_array()` tiene auto-stretch redundante en algunos estilos
4. **harnesses.py** — `sys.path.insert(0, _src)` hardcodeado en kernel.py (circular import problem)
5. **No hay pyproject.toml/requirements.txt** — dependencias no declaradas formalmente

---

## 2. EVALUACIÓN DE CADA FEATURE PROPUESTA

### 🟢 ESENCIAL (debe tener)

#### 2.1 Coordenadas Normalizadas (0-100)
**¿Por qué?** Es el cimiento de todo lo demás. Sin coordenadas normalizadas, el OCR y la jerarquía visual son inútiles.
**Coste:** ~30 líneas. Los BBox ya son [0-1], solo escalar ×100.
**Implementación:** Añadir a `SceneNode` y a cada detección.
```python
@dataclass
class SceneNode:
    # ... existente ...
    @property
    def bbox_normalized_100(self) -> dict:
        return {"x0": int(self.bbox.x0*100), "y0": int(self.bbox.y0*100),
                "x1": int(self.bbox.x1*100), "y1": int(self.bbox.y1*100)}
```

#### 2.2 OCR con Tesseract
**¿Por qué?** El 60%+ de las imágenes que un LLM necesita "ver" contienen texto (interfaces, documentos, capturas, memes con texto). Sin OCR, Samson Vision es ciego al contenido textual.
**¿Tesseract?** SÍ, pero vía `pytesseract`. En Linux es la opción más madura y probada.
- `pytesseract` wrapper → `ocr_with_coords(image)` → devuelve texto + bounding boxes
- Alternativa: `easyocr` (más pesado, GPU opcional, mejor para multi-idioma)
- **Recomendación:** pytesseract como base, easyocr como fallback para CJK
**Coste:** ~80 líneas + `apt install tesseract-ocr tesseract-ocr-spa`

#### 2.3 Samson Vision Pack (formato unificado)
**¿Por qué?** Sin un formato de salida unificado, cada componente produce datos incompletos. El VB Pack es el contrato entre Samson Vision y el consumidor (LLM, API, interfaz).
**Coste:** ~100 líneas (schema + serializer).
**Propuesta de schema más abajo.

#### 2.4 Instrucciones de interpretación para IA sin visión
**¿Por qué?** Es el "traductor final" — convierte los datos brutos del VB Pack en instrucciones claras que un LLM de texto puede seguir sin ambigüedad.
**Coste:** ~60 líneas (template engine simple).
**Implementación:** Función `generate_interpretation_instructions(pack)` que produce texto tipo:
```
La imagen contiene 3 regiones principales:
1. [40-80, 10-50] (25% del área) — Rectángulo rojo (RGB 255,68,68), forma geométrica
2. [10-40, 10-50] (15% del área) — Zona azul con texto "SV2"
...
```

#### 2.5 Paleta de colores textual con modificadores
**¿Por qué?** El análisis de color actual solo dice "RGB(128,64,32)". Los LLMs entienden mejor "rojo cálido intenso" que "RGB(200,50,30)".
**Coste:** ~40 líneas.
**Implementación:** Mapper RGB → nombre textual + modificadores (brillo, saturación, temperatura).

### 🟡 VALIOSO (añadir después del core)

#### 2.6 Detección de movimiento entre frames
**¿Por qué?** Permite a un LLM entender dinámica: "algo se mueve de izquierda a derecha", "la interfaz cambió".
**Coste:** ~80 líneas (diferencia frame-to-frame + umbral).
**Implementación:** `MotionDetector` que compara dos VB Packs y produce delta.
**Prioridad:** Media. Solo útil para video/streaming. Para imágenes estáticas, no aporta.

#### 2.7 Patrones de movimiento
**¿Por qué?** Clasificar movimiento en categorías textuales (STATIC, BLINK, SLIDE, GROW, ROTATE) es útil para LLMs.
**Coste:** ~50 líneas sobre el MotionDetector.
**Prioridad:** Baja-Media. Solo con video.

#### 2.8 Jerarquía visual (niveles 1-5)
**¿Por qué?** Permite al LLM priorizar: "mira primero la zona de nivel 5, luego las demás".
**Coste:** ~40 líneas.
**Implementación:** Calcular importancia por: tamaño × contraste × posición central × saliency.
**Prioridad:** Alta. Es complementario a saliency que ya existe.

#### 2.9 Layout por densidad visual (density map)
**¿Por qué?** Divide la imagen en cuadrícula y reporta densidad visual por celda. Ayuda al LLM a entender la distribución espacial.
**Coste:** ~30 líneas.
**Implementación:** Grid NxN, calcular entropía/gradiente por celda.
**Prioridad:** Media.

### 🔴 RUIDO (no implementar aún)

#### 2.10 Chafa — NO HACER
**¿Por qué?** Chafa es una CLI externa (subprocess) que hace conversión ANSI/Unicode. Samson_core.py YA hace esto mejor:
- 8 estilos vs Chafa's ~3 modos
- Chafa es C con dependencias glib/GDK
- Añadiría dependencia del sistema sin beneficio real
- **Alternativa:** Si se necesita algo de Chafa, usar `subprocess.run(["chafa", ...])` como harness, no integrar
**Veredicto:** ❌ Ruido. samson_core.py es superior para este caso de uso.

#### 2.11 OpenCV — NO HACER (aún)
**¿Por qué?** OpenCV es enorme (~200MB), tiene dependencias C++ complejas, y el 80% de lo que se necesita ya está en numpy+PIL:
- Contornos → ya hace `detect_objects_simple()` con diff de color
- Detección de objetos reales → requiere modelos YOLO/etc (mucho más allá de OpenCV)
- Detección de bordes → ya tiene Sobel en kernel.py
**¿Cuándo sí?** Solo si se necesita:
- HOG descriptor para detección de personas
- Template matching preciso
- Procesamiento de video real-time
**Veredicto:** ❌ Por ahora, numpy+PIL cubre el 80%.

#### 2.12 HTML visual simplificado
**¿Por qué?** Generar HTML a partir de los datos ya disponibles es trivial (~20 líneas) pero no es prioritario.
**Coste:** Bajo, pero es output formatting, no core logic.
**Veredicto:** ⏳ Hacerlo como utilidad final, no como componente core.

---

## 3. PRIORIZACIÓN PROPUESTA

### Fase 1 — Foundation (1-2 días)
```
1. Coordenadas normalizadas (0-100)     → 30 líneas
2. Paleta de colores textual            → 40 líneas  
3. Samson Vision Pack schema            → 100 líneas
4. Instrucciones de interpretación      → 60 líneas
5. Refactor: limpiar imports circulares  → 20 líneas
6. pyproject.toml con dependencias      → 15 líneas
```

### Fase 2 — Intelligence (2-3 días)
```
7. OCR con Tesseract (pytesseract)      → 80 líneas + apt install
8. Jerarquía visual (1-5)               → 40 líneas
9. Density map                          → 30 líneas
10. HTML visual como utilidad           → 40 líneas
```

### Fase 3 — Motion (1-2 días)
```
11. MotionDetector (frame diff)         → 80 líneas
12. Patrones de movimiento              → 50 líneas
13. Video pipeline                      → 60 líneas
```

---

## 4. VISION BRIDGE PACK — Schema Propuesto

```json
{
  "$schema": "vision-bridge-pack/1.0",
  "meta": {
    "version": "1.0",
    "source": "samson-vision/3.0",
    "timestamp": "2025-06-23T12:00:00Z",
    "image": {
      "original_size": [1920, 1080],
      "aspect_ratio": 1.778,
      "format": "png"
    }
  },
  "ascii_art": {
    "standard": "...",
    "edge": "...",
    "braille": "...",
    "best_for_llm": "..."
  },
  "regions": [
    {
      "id": "r0",
      "label": "rectangular_region",
      "bbox_100": {"x0": 10, "y0": 13, "x1": 42, "y1": 53},
      "area_pct": 16.8,
      "importance": 4,
      "color": {"rgb": [255, 68, 68], "textual": "rojo saturado", "temperature": "cálido"},
      "ocr_text": null,
      "confidence": 0.92
    },
    {
      "id": "r1",
      "label": "text_region",
      "bbox_100": {"x0": 5, "y0": 3, "x1": 20, "y1": 10},
      "area_pct": 3.5,
      "importance": 5,
      "color": {"rgb": [51, 51, 51], "textual": "gris oscuro", "temperature": "neutro"},
      "ocr_text": "SV2",
      "ocr_confidence": 0.98,
      "confidence": 0.95
    }
  ],
  "scene_graph": {
    "n_nodes": 3,
    "n_relations": 5,
    "relations": ["r0 near r1", "r0 overlaps r2"]
  },
  "analysis": {
    "color_tone": "mixto",
    "brightness": "medio",
    "contrast": "alto",
    "edge_complexity": "media",
    "dominant_direction": "mixto/diagonal",
    "focus_point": {"x": 55, "y": 30},
    "n_unique_colors": 42
  },
  "density_map": {
    "grid": "4x4",
    "cells": [
      {"x": 0, "y": 0, "density": 0.3, "label": "baja"},
      {"x": 1, "y": 0, "density": 0.8, "label": "alta"}
    ]
  },
  "motion": {
    "type": "STATIC",
    "delta_from_previous": null
  },
  "interpretation": {
    "for_blind_ai": "La imagen contiene 3 regiones principales sobre fondo gris claro. La región más prominente (25% del área, nivel 5) es un rectángulo rojo saturado en la parte superior izquierda...",
    "summary_50_words": "Imagen con formas geométricas: rectángulo rojo, círculo azul, triángulo verde sobre fondo gris. Texto 'SV2' visible."
  }
}
```

---

## 5. ANÁLISIS DE CHAFA vs SAMSON_CORE

| Aspecto | Chafa | samson_core |
|---|---|---|
| Estilos | 3 (fitted, tile, unicode) | 8 (standard, detail, block, edge, dither, fanart, braille, color) |
| Densidad | Fija por --size | Variable por estilo + auto-stretch |
| Color | Sí (256/truecolor ANSI) | Sí (truecolor ANSI en style=color) |
| Braille | Limitado | Implementación completa 4x2 |
| Dependencias | C, glib, GDK, ImageMagick | Solo numpy + PIL |
| Tamaño | ~50MB instalado | 0MB extra |
| Extensible | No (C binary) | Sí (Python puro) |
| Velocidad | Más rápido en C | Más lento pero suficiente |
| Uso como lib | CLI subprocess | Import directo |

**Conclusión:** Chafa no aporta nada que samson_core no tenga. Si acaso, el estilo `color` de samson_core es equivalente a `chafa --format=iterm2`. La única ventaja de Chafa es velocidad en procesamiento batch de miles de imágenes, pero para el caso de uso de Samson Vision (análisis individual por LLM), no es relevante.

**Recomendación:** NO integrar Chafa. En su lugar, mejorar samson_core:
- Añadir estilo `sixel` (si terminal lo soporta)
- Añadir estilo `kitty` (graphics protocol)
- Añadir estilo `hybrid` (edge + color combinado)

---

## 6. TESSERACT vs ALTERNATIVAS

| OCR | Precisión | Velocidad | Multi-idioma | Dependencias | GPU |
|---|---|---|---|---|---|
| **pytesseract** | 85-95% | ~200ms/img | 100+ idiomas | tesseract-ocr (apt) | No |
| **easyocr** | 90-98% | ~2s/img | 80+ idiomas | PyTorch (~2GB) | Opcional |
| **surya-ocr** | 95-99% | ~1s/img | 90+ idiomas | PyTorch (~2GB) | Sí (recomendado) |
| **rapidocr** | 85-92% | ~100ms/img | 50+ idiomas | onnxruntime | No |
| **fast-ocr** (npm) | 80-90% | ~150ms/img | 20+ idiomas | Node.js | No |

**Recomendación para Samson Vision:**
1. **Primario: pytesseract** — Instalación trivial (`apt install tesseract-ocr tesseract-ocr-spa tesseract-ocr-eng`), sin dependencias Python pesadas, suficiente para el 90% de casos
2. **Fallback: easyocr** — Solo si pytesseract falla en idiomas no latinos (CJK, árabe)
3. **NO surya/rapidocr** — Para un sistema de 2000 líneas, añadir PyTorch es desproporcionado

**pytesseract con coordenadas:**
```python
import pytesseract
from PIL import Image

def ocr_with_coordinates(image: Image.Image) -> list:
    """Extrae texto + bounding boxes normalizados (0-100)."""
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    results = []
    w, h = image.size
    for i, text in enumerate(data['text']):
        if text.strip():
            results.append({
                'text': text,
                'bbox_100': {
                    'x0': int(data['left'][i] / w * 100),
                    'y0': int(data['top'][i] / h * 100),
                    'x1': int((data['left'][i] + data['width'][i]) / w * 100),
                    'y1': int((data['top'][i] + data['height'][i]) / h * 100),
                },
                'confidence': data['conf'][i] / 100.0,
                'block': data['block_num'][i],
                'line': data['line_num'][i],
            })
    return results
```

---

## 7. OPENCV — ¿CUÁNDO SÍ?

OpenCV se justifica SOLO si se necesita:
1. **Detección de caras** (Haar cascades) → pero hay librerías más ligeras
2. **Template matching** → numpy puede hacer `np.correlate` para esto
3. **Video processing real-time** → frames > 30fps
4. **Undistortion de cámaras** → caso muy específico
5. **Detección de contornos precisa** → el `detect_objects_simple()` actual es aproximado

**El caso actual de detección de objetos** en kernel.py usa diff de color + grid scanning. Para imágenes con formas geométricas claras, funciona. Para fotos reales con objetos complejos, necesitaría YOLO/SSD (que SÍ requiere OpenCV o similar).

**Recomendación:** 
- **NO instalar OpenCV como dependencia core**
- Crear un `harness_opencv.py` que lo use opcionalmente: `if opencv_available: ... else: fallback_numpy`
- Para detección de objetos reales → delegar a un VLM externo (GPT-4V, Claude Vision) vía harnesses

---

## 8. JERARQUÍA VISUAL — Diseño

```python
def calculate_importance(region, saliency_map, image_center):
    """
    Calcula importancia 1-5 de una región.
    
    Factor 1: Área (más grande = más importante)
    Factor 2: Contraste con vecinos (más contraste = más importante)
    Factor 3: Proximidad al centro (más centrada = más importante)
    Factor 4: Saliency (ya calculado por VMK)
    Factor 5: Contiene texto (OCR boost)
    """
    area_score = min(5, region.area_pct / 5)  # 25% → 5.0
    contrast_score = min(5, region.edge_density * 30)
    center_dist = sqrt((region.cx - 50)**2 + (region.cy - 50)**2)
    center_score = max(0, 5 - center_dist / 10)
    saliency_score = region.saliency_value * 5
    text_boost = 2 if region.ocr_text else 0
    
    raw = (area_score + contrast_score + center_score + 
           saliency_score + text_boost) / 4
    return max(1, min(5, round(raw)))
```

---

## 9. DENSITY MAP — Diseño

```python
def compute_density_map(image, grid_w=4, grid_h=4):
    """
    Divide imagen en grid y calcula densidad visual por celda.
    
    Densidad = varianza de gradiente + varianza de color + presencia de bordes.
    """
    gray = np.array(image.convert('L'))
    h, w = gray.shape
    cell_h, cell_w = h // grid_h, w // grid_w
    
    cells = []
    for gy in range(grid_h):
        for gx in range(grid_w):
            cell = gray[gy*cell_h:(gy+1)*cell_h, gx*cell_w:(gx+1)*cell_w]
            
            # Gradiente local
            gx_deriv = np.abs(np.diff(cell.astype(float), axis=1))
            gy_deriv = np.abs(np.diff(cell.astype(float), axis=0))
            
            density = float(np.mean(gx_deriv) + np.mean(gy_deriv))
            level = "alta" if density > 30 else "media" if density > 10 else "baja"
            
            cells.append({
                "grid_x": gx, "grid_y": gy,
                "bbox_100": {
                    "x0": int(gx/grid_w*100), "y0": int(gy/grid_h*100),
                    "x1": int((gx+1)/grid_w*100), "y1": int((gy+1)/grid_h*100)
                },
                "density": round(density, 2),
                "level": level
            })
    
    return {"grid": f"{grid_w}x{grid_h}", "cells": cells}
```

---

## 10. MOTION DETECTION — Diseño

```python
@dataclass
class MotionResult:
    type: str  # STATIC, BLINK, SLIDE_LEFT, SLIDE_RIGHT, GROW, SHRINK, ROTATE, CHAOS
    intensity: float  # 0.0 - 1.0
    direction: Optional[tuple]  # (dx, dy) normalizado
    speed: Optional[float]  # pixels por frame
    changed_regions: list  # IDs de regiones que cambiaron

class MotionDetector:
    def __init__(self):
        self._prev_pack: Optional[dict] = None
    
    def detect(self, current_pack: dict) -> MotionResult:
        if self._prev_pack is None:
            self._prev_pack = current_pack
            return MotionResult(type="STATIC", intensity=0.0, 
                              direction=None, speed=None, changed_regions=[])
        
        # Comparar ASCII art pixel por pixel (como proxy de diferencia visual)
        prev_ascii = self._prev_pack.get("ascii_art", {}).get("standard", "")
        curr_ascii = current_pack.get("ascii_art", {}).get("standard", "")
        
        # Calcular Hamming distance normalizada
        min_len = min(len(prev_ascii), len(curr_ascii))
        if min_len == 0:
            return MotionResult(type="CHAOS", intensity=1.0, ...)
        
        diffs = sum(1 for a, b in zip(prev_ascii[:min_len], curr_ascii[:min_len]) if a != b)
        intensity = diffs / min_len
        
        if intensity < 0.02:
            motion_type = "STATIC"
        elif intensity < 0.1:
            # Detectar dirección: comparar regiones shifted
            motion_type = self._classify_direction(prev_pack, current_pack)
        else:
            motion_type = "CHAOS" if intensity > 0.5 else "CHANGE"
        
        self._prev_pack = current_pack
        return MotionResult(type=motion_type, intensity=intensity, ...)
```

---

## 11. ESTRUCTURA DE ARCHIVOS PROPUESTA

```
samson-vision/
├── src/
│   ├── samson_core.py          # ✅ Exists — 8 estilos + visual language
│   ├── device_db.py            # ✅ Exists — device DB
│   ├── synesthesia.py          # ✅ Exists — audio visualization
│   ├── harnesses.py            # ✅ Exists — LLM integrations
│   ├── vmk/
│   │   ├── __init__.py
│   │   ├── kernel.py           # ✅ Exists — orquestador
│   │   ├── scene_graph.py      # ✅ Exists — grafo de escena
│   │   ├── ocr.py              # 🆕 pytesseract wrapper
│   │   ├── motion.py           # 🆕 detección de movimiento
│   │   └── density.py          # 🆕 density map
│   ├── samson_vision.py        # 🆕 Samson Vision Pack + serializer
│   ├── palette.py              # 🆕 paleta de colores textual
│   ├── hierarchy.py            # 🆕 jerarquía visual 1-5
│   └── interpretation.py       # 🆕 instrucciones para IA ciega
├── test/
│   └── run_tests.py            # ✅ Exists — 29 tests
├── pyproject.toml              # 🆕 dependencias declaradas
└── SAMSON_VISION_ARCHITECTURE.md  # 🆕 este documento
```

---

## 12. RESPUESTAS A PREGUNTAS CLAVE

### Q1: ¿Qué es esencial vs ruido?

| Feature | Veredicto | Razón |
|---|---|---|
| Coordenadas 0-100 | 🟢 Esencial | Cimiento de todo |
| OCR (Tesseract) | 🟢 Esencial | 60%+ imágenes tienen texto |
| VB Pack | 🟢 Esencial | Formato de salida unificado |
| Instrucciones IA | 🟢 Esencial | Traductor final LLM |
| Paleta textual | 🟢 Esencial | Comprensión LLM mejorada |
| Jerarquía visual | 🟡 Valioso | Priorización de atención |
| Density map | 🟡 Valioso | Distribución espacial |
| HTML visual | 🟡 Valioso | Utilidad, no core |
| Motion detect | 🟠 Opcional | Solo para video |
| Motion patterns | 🟠 Opcional | Solo para video |
| OpenCV | 🔴 Ruido (ahora) | numpy+PIL cubre |
| Chafa | 🔴 Ruido | samson_core es superior |

### Q2: ¿Prioridad?

**Sprint 1 (Foundation):** Coordenadas → Colores textuales → VB Pack → Interpretación → Refactor
**Sprint 2 (Intelligence):** OCR → Jerarquía → Density → HTML
**Sprint 3 (Motion):** MotionDetector → Patterns → Video

### Q3: ¿Samson Vision Pack?

Ver sección 4. JSON con 6 secciones: meta, ascii_art, regions, analysis, density_map, interpretation.

### Q4: ¿Chafa aporta?

NO. samson_core.py tiene 8 estilos vs Chafa's 3. Sin dependencias C/glib/GDK. Extensible en Python. Para Samson Vision, Chafa es redundante.

### Q5: ¿Tesseract o alternativa?

pytesseract es correcto para Linux. Trivial de instalar (`apt install tesseract-ocr`), soporta 100+ idiomas, devuelve coordenadas via `image_to_data()`. No necesita GPU ni PyTorch. Para CJK, añadir easyocr como fallback opcional.

---

## 13. MÉTRICAS DE ÉXITO

| Métrica | v2.0 Actual | v3.0 Target |
|---|---|---|
| Tests | 29/29 | 45+/45+ |
| Líneas totales | ~2100 | ~3000 |
| Dependencias Python | numpy, PIL | +pytesseract |
| Dependencias system | Ninguna | +tesseract-ocr |
| Tiempo análisis/img | ~50ms | ~250ms (+OCR) |
| Formato salida | Texto libre | JSON estructurado |
| Multi-frame | No | Sí (motion) |
| Texto en imagen | No detectado | OCR con coordenadas |
| Importancia | No cuantificada | Niveles 1-5 |
| Dense map | No | 4x4 grid |
| Para LLM ciego | Parcial | Completo |

---

*Análisis generado por Hermes Agent — 2025-06-23*
