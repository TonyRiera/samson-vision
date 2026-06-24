# 01 — Output Schema

Toda salida debe usar:

```text
[SAMSON_VISION_PACK v1]

IMAGE_TYPE:
GLOBAL_SUMMARY:
VISUAL_HIERARCHY:
LAYOUT_MAP:
OCR_TEXT:
OBJECTS_AND_COMPONENTS:
COLOR_MAP:
DENSITY_MAP:
ASCII_REPRESENTATION:
USER_ACTIONS:
UNCERTAINTIES:
DO_NOT_ASSUME:
FINAL_INTERPRETATION_FOR_TEXT_ONLY_AI:
```

## Campos

- `IMAGE_TYPE`: tipo, calidad, recorte y dominio.
- `GLOBAL_SUMMARY`: resumen breve y fiel.
- `VISUAL_HIERARCHY`: orden de importancia visual.
- `LAYOUT_MAP`: zonas con coordenadas `[x1,y1,x2,y2]`.
- `OCR_TEXT`: texto visible, coordenadas y confianza.
- `OBJECTS_AND_COMPONENTS`: botones, campos, tablas, iconos, alertas.
- `COLOR_MAP`: colores dominantes y semánticos.
- `DENSITY_MAP`: zonas densas, vacías o saturadas.
- `ASCII_REPRESENTATION`: mapa útil, no decorativo.
- `USER_ACTIONS`: acciones posibles y coordenadas.
- `UNCERTAINTIES`: dudas explícitas.
- `DO_NOT_ASSUME`: cosas que el modelo texto no debe inventar.
- `FINAL_INTERPRETATION_FOR_TEXT_ONLY_AI`: síntesis segura.

