[SAMSON_VISION_PACK v1]

IMAGE_TYPE:
- domain: photo
- subtype: indoor scene
- quality: medium
- crop: complete

GLOBAL_SUMMARY:
- Foto de una mesa de trabajo con un portátil abierto, una taza y varios objetos pequeños alrededor.

VISUAL_HIERARCHY:
- [20,25,78,70] portátil abierto en el centro.
- [8,55,22,75] taza a la izquierda.
- [70,72,92,88] libreta u objeto rectangular en la parte inferior derecha.

LAYOUT_MAP:
- [0,0,100,100] escena completa.
- [20,25,78,70] laptop_area.
- [0,70,100,100] foreground_table_edge.

OCR_TEXT:
- No visible text, confidence high.

OBJECTS_AND_COMPONENTS:
- laptop at [20,25,78,70], screen open, content not legible.
- cup at [8,55,22,75], cylindrical object.
- notebook_or_pad at [70,72,92,88], rectangular object, function uncertain.

COLOR_MAP:
- table: brown_light.
- laptop: gray_dark/black.
- cup: white.

DENSITY_MAP:
- Center medium density.
- Foreground medium density.
- Background low density.

ASCII_REPRESENTATION:
```text
+------------------------------------------------+
|                                                |
|              [ laptop screen ]                 |
|              [ keyboard area ]                 |
|  cup                                   notebook |
+------------------------------------------------+
```

USER_ACTIONS:
- If task needs screen content, request closer crop of [20,25,78,70].
- If task needs object inventory, central objects are visible enough for a rough list.

UNCERTAINTIES:
- Screen content is not legible.
- Rectangular object may be notebook or tablet; confidence low.

DO_NOT_ASSUME:
- Do not identify owner.
- Do not infer exact location.
- Do not read screen content.

FINAL_INTERPRETATION_FOR_TEXT_ONLY_AI:
- The scene is a workspace photo. It supports spatial/object reasoning, but not reading screen content or identifying people/location.

