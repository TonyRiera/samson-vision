# Architecture

## Overview

Samson Vision is a **purely algorithmic image-to-text pipeline** with zero AI dependency. The entire pipeline — from image input to VBP output — uses only numpy, OpenCV, and Tesseract. AI models are only called to *interpret* the resulting VBP, not to generate it.

## Pipeline

```
┌─────────────┐    ┌──────────────┐    ┌──────────────┐    ┌─────────────┐
│   Image     │───▶│  samson_core │───▶│ samson_vision│───▶│   VBP       │
│  (any fmt)  │    │  (8 styles)  │    │  (13 fields) │    │  (text)     │
└─────────────┘    └──────────────┘    └──────────────┘    └─────────────┘
                        │                     │
                        ▼                     ▼
                 ┌──────────────┐    ┌──────────────┐
                 │  VMK Kernel  │    │  Tesseract   │
                 │  (OpenCV)    │    │  OCR         │
                 │  ┌─────────┐ │    │  ┌─────────┐ │
                 │  │Scene    │ │    │  │span+eng │ │
                 │  │Graph    │ │    │  │OTSU 2x  │ │
                 │  └─────────┘ │    │  │Line grp │ │
                 └──────────────┘    └──────────────┘
```

### Stage 1: ASCII Conversion (samson_core.py)

Converts any image to ASCII art in 8 styles:

1. **standard** — 10-level density palette (`@%#*+=-:. `)
2. **detail** — 22-level extended palette for precision
3. **block** — Unicode block characters (`██▄▀`)
4. **edge** — Edge detection + ASCII hybrid
5. **color** — ANSI color codes + ASCII (terminal output)
6. **dither** — Floyd-Steinberg dithering
7. **fanart** — Inverted density, creative patterns
8. **braille** — Unicode Braille patterns (`⣿⣧⣄`)

Each style captures different aspects: standard for quick overview, detail for precision, edge for structure, braille for compression.

### Stage 2: Vision Multimodal Kernel (vmk/)

Processes images through four parallel analysis modules:

**Color Analysis**
- Average RGB, brightness, contrast
- Dominant colors with human-readable names
- Tone classification (warm, cool, neutral)

**Edge Analysis** (OpenCV Canny)
- Edge intensity and density
- Complexity score
- Dominant direction (horizontal, vertical, diagonal)

**Saliency Detection**
- Focus point (center of visual weight)
- Hot zone fraction (how much of the image is "busy")
- Attention map via contrast variance

**Scene Graph**
- Object detection via contour analysis
- Spatial relationships (left_of, above, contains, overlaps, near)
- Bounding boxes normalized to 0-100

### Stage 3: OCR (samson_vision.py)

**Tesseract OCR** with image preprocessing:
- 2x upscale (LANCZOS) for small text
- Grayscale conversion
- Contrast enhancement (1.5x)
- OTSU binarization (adaptive threshold)
- Line grouping (words merged by Y-coordinate)
- Spanish + English language models
- Confidence filtering (≥0.4 threshold)

### Stage 4: VBP Assembly (samson_vision.py)

Combines all previous stages into the 13-field SAMSON_VISION_PACK format. See [SAMSON_VISION_PACK.md](SAMSON_VISION_PACK.md) for the complete specification.

## Data flow

```python
# Simplified flow
img = load_image(path)
ascii = convert_all_styles(img)              # 8 ASCII representations
vmk_report = vmk.process_image_multimodal(img) # Color, edges, objects, scene graph
text = detect_text_tesseract(img)             # OCR with preprocessing
vbp = assemble_vbp(ascii, vmk_report, text)  # 13-field structured pack
```

## Server architecture

The optional HTTP server (`samson_vision_server.py`) provides OpenAI-compatible endpoints:

```
GET  /health          → Server status
GET  /v1/models       → Available models/styles
POST /v1/vision/ascii → ASCII art (specific style)
POST /v1/vision/language → Multi-layer visual language
POST /v1/vision/analyze  → VMK analysis + scene graph
POST /v1/bridge       → Full SAMSON_VISION_PACK ← MAIN ENDPOINT
POST /v1/chat/completions → OpenAI-compatible chat
```

## Dependencies

| Library | Required | Purpose |
|---------|:--------:|---------|
| pillow | ✅ | Image loading and basic manipulation |
| numpy | ✅ | Array operations, pixel processing |
| opencv-python-headless | ❌ | Canny edge detection, contour analysis |
| pytesseract | ❌ | OCR text extraction |
| tesseract binary | ❌ | OCR engine |

The system degrades gracefully: without OpenCV it uses numpy fallbacks, without Tesseract it uses simple contrast-based text zone detection.
