# SAMSON_VISION_PACK — Complete Specification

> Version 1.0 | The core of Samson Vision

## What is a SAMSON_VISION_PACK?

A SAMSON_VISION_PACK (SVP) is a **structured text representation of an image** designed for consumption by text-only LLMs. It transforms visual information into 13 complementary textual fields that together allow a model to reconstruct a mental image with high fidelity.

Unlike ASCII art alone (which loses color, small text, and spatial relationships), the SVP combines multiple representation layers that compensate for each other's weaknesses.

## Why Samson Vision?

Sansón perdió la **vista física**, pero recuperó la **visión del plan de Dios** (Jueces 16:28-30). No necesitaba ver el templo — necesitaba saber **cuándo y cómo actuar**. Samson Vision aplica la misma idea a agentes de IA: tu modelo **sigue sin ojos** (sin modelo de visión), pero recibe **visión** a través del SVP — 13 campos de texto que codifican la verdad estructural que los píxeles esconden. Los modelos con visión nativa son caros, a menudo más débiles en código y razonamiento, y cambiar de agente borra el contexto. SVP permite que cualquier LLM de texto "vea" sin cambiar de modelo ni pagar APIs de visión.

*Samson lost physical sight but gained vision of God's plan. The AI still has no eyes — Samson Vision gives it sight through SVP text anyway.*


## The 13 Fields

### 1. IMAGE_TYPE

Basic metadata about the image.

```
IMAGE_TYPE:
- domain: web|document|photograph|screenshot|dashboard|generic
- subtype: specific classification
- quality: low|medium|high
- dimensions: width x height in pixels
- aspect_ratio: width/height
```

**Purpose:** Tells the model what kind of image it's looking at, setting expectations.

### 2. GLOBAL_SUMMARY

A one-to-two sentence overview of the image.

```
GLOBAL_SUMMARY:
- The image contains [N] visual regions. Overall tone: [description].
```

**Purpose:** Quick orientation. The model knows what to expect before diving into details.

### 3. VISUAL_HIERARCHY

Elements ordered by visual importance (level 1 = most important).

```
VISUAL_HIERARCHY:
- [x1,y1,x2,y2] element_label (level N)
```

**Purpose:** Tells the model what to focus on first. Mirror's human visual attention.

### 4. LAYOUT_MAP

All detected zones with their positions (0-100 scale).

```
LAYOUT_MAP:
- [x1,y1,x2,y2] zone_label
```

**Purpose:** Spatial awareness — where things are located in the image.

### 5. OCR_TEXT

Text detected via Tesseract OCR with position and confidence.

```
OCR_TEXT:
- "detected text" at [x1,y1,x2,y2], confidence high|medium|low
```

**Purpose:** Readable text content. The model gets the actual words, not just shapes.

### 6. OBJECTS_AND_COMPONENTS

Detected visual elements with their positions and sizes.

```
OBJECTS_AND_COMPONENTS:
- label at [x1,y1,x2,y2], area N%
```

**Purpose:** What things are, not just where they are.

### 7. COLOR_MAP

Dominant colors with human-readable names.

```
COLOR_MAP:
- color_name: percentage%
```

**Purpose:** Color understanding without color vision. Maps RGB values to named colors.

### 8. DENSITY_MAP

Visual density by horizontal bands (10% increments).

```
DENSITY_MAP:
- y=N%: density low|medium|high
```

**Purpose:** Content distribution — where the "busy" areas are.

### 9. ASCII_REPRESENTATION

Multi-style ASCII art for shape and structure understanding.

```
ASCII_REPRESENTATION:
```text
[ASCII art here]
```
```

**Purpose:** Provides texture, shape, and spatial relationships that text alone can't convey. Uses 8 styles: standard, detail, block, edge, dither, fanart, braille.

### 10. USER_ACTIONS

Suggested interaction points with coordinates.

```
USER_ACTIONS:
- Interact with element_label at [cx,cy]
```

**Purpose:** For UI/images with interactive elements. Helps model reason about functionality.

### 11. UNCERTAINTIES

Explicit limitations of what was detected.

```
UNCERTAINTIES:
- List of what the system is unsure about
```

**Purpose:** Anti-hallucination. The model knows the limits of the detection.

### 12. DO_NOT_ASSUME

Things the model must not invent.

```
DO_NOT_ASSUME:
- Do not assume readable text where OCR didn't confirm it
- Do not assume functionality of unlabeled elements
- Do not assume content outside the visible area
```

**Purpose:** Hard guardrails against hallucination.

### 13. FINAL_INTERPRETATION_FOR_TEXT_ONLY_AI

A synthesis designed specifically for text-only models.

```
FINAL_INTERPRETATION_FOR_TEXT_ONLY_AI:
- Key facts the model can safely use
```

**Purpose:** A "safe path" — the minimum reliable information the model can build upon.

## Output Formats

The SVP can be generated in two formats:

### Markdown (--md)
Human-readable, structured with headers and sections. Best for feeding to LLMs as context.

### JSON (--json)
Machine-parseable with all fields as structured data. Best for programmatic processing.

## Coordinate System

All spatial coordinates use a **normalized 0-100 scale** (percentage of image dimensions).

- `[0,0]` = top-left corner
- `[100,100]` = bottom-right corner
- Elements are specified as `[x1,y1,x2,y2]` where (x1,y1) is top-left and (x2,y2) is bottom-right

This allows comparison across images of different sizes.

## Confidence Levels

| Level | Threshold | Meaning |
|-------|:---------:|---------|
| high | > 0.8 | Reliable detection |
| medium | 0.5 - 0.8 | Probable but uncertain |
| low | < 0.5 | Speculative, may be noise |

## Anti-Hallucination Design

The SVP includes **three specific anti-hallucination mechanisms**:

1. **UNCERTAINTIES** — explicit limits of detection quality
2. **DO_NOT_ASSUME** — hard rules against common hallucination patterns
3. **Confidence labels** — per-element confidence on OCR and object detection

These are not optional. A valid SVP MUST include all three.
