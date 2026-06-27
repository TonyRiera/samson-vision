[SAMSON_VISION_PACK v1]

IMAGE_TYPE:
- domain: web
- subtype: generic
- quality: medium
- dimensions: 1024x1536
- aspect_ratio: 0.667

GLOBAL_SUMMARY:
- La imagen contiene 20 regiones visuales detectadas. Tonalidad general: mixto. La imagen tiene complejidad visual alta. Se detectaron 6 zonas de texto. Nivel 1 (PRINCIPAL): 3 elementos. Nivel 3 (DETALLE): 17 elementos.

VISUAL_HIERARCHY:
- [0,63,90,96] medium_region (nivel 1)
- [49,8,85,60] medium_region (nivel 1)
- [18,12,50,60] medium_region (nivel 1)
- [85,24,100,36] tiny_region (nivel 3)
- [24,83,37,94] tiny_region (nivel 3)
- [0,81,14,90] tiny_region (nivel 3)
- [84,76,96,82] tiny_region (nivel 3)
- [2,19,14,26] tiny_region (nivel 3)
- [68,65,78,70] tiny_region (nivel 3)
- [17,85,27,89] tiny_region (nivel 3)

LAYOUT_MAP:
- [0,63,90,96] medium_region
- [49,8,85,60] medium_region
- [18,12,50,60] medium_region
- [85,24,100,36] tiny_region
- [24,83,37,94] tiny_region
- [0,81,14,90] tiny_region
- [84,76,96,82] tiny_region
- [2,19,14,26] tiny_region
- [68,65,78,70] tiny_region
- [17,85,27,89] tiny_region
- [6,74,16,78] tiny_region
- [50,85,58,90] tiny_region
- [9,84,18,89] tiny_region
- [19,77,27,82] tiny_region
- [73,92,80,98] tiny_region

OCR_TEXT:
- "[text_zone]" at [30,10,40,20], confidence medium
- "[text_zone]" at [20,40,40,50], confidence medium
- "[text_zone]" at [50,40,80,50], confidence medium
- "[text_zone]" at [40,80,60,100], confidence medium
- "[text_zone]" at [60,80,70,90], confidence medium
- "[text_zone]" at [40,90,50,100], confidence medium

OBJECTS_AND_COMPONENTS:
- medium_region at [0,63,90,96], area 29%
- medium_region at [49,8,85,60], area 19%
- medium_region at [18,12,50,60], area 16%
- tiny_region at [85,24,100,36], area 2%
- tiny_region at [24,83,37,94], area 1%
- tiny_region at [0,81,14,90], area 1%
- tiny_region at [84,76,96,82], area 1%
- tiny_region at [2,19,14,26], area 1%
- tiny_region at [68,65,78,70], area 1%
- tiny_region at [17,85,27,89], area 0%
- tiny_region at [6,74,16,78], area 0%
- tiny_region at [50,85,58,90], area 0%
- tiny_region at [9,84,18,89], area 0%
- tiny_region at [19,77,27,82], area 0%
- tiny_region at [73,92,80,98], area 0%

COLOR_MAP:
- black: 58%
- gray_dark: 16%
- gray_dark: 14%
- brown_medium: 5%
- orange_medium: 2%
- red_medium: 2%

DENSITY_MAP:
- y=0%: densidad alta
- y=10%: densidad alta
- y=20%: densidad alta
- y=30%: densidad alta
- y=40%: densidad alta
- y=50%: densidad alta
- y=60%: densidad alta
- y=70%: densidad alta
- y=80%: densidad alta
- y=90%: densidad alta

ASCII_REPRESENTATION:
```text
@@@@@@@@@@@@@@@@@@@%%%%%%%###*+==-:.. . .....::=+*##%%%%@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@%%%%%####**+==-::......:::--=+*###%%%%@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@%%%%%%####**+==--:::::::------===+***###%%@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@%%%%%%##*+==--:::::::::--:::::::-==+*####%%%%%@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@%%%##*++=---::::::...:::...:::--==++**###%%%%#%@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@%%%#******++==-----:-:::.:::----==++***###%%%%%%@@@@@@@@@@@@@@@
```

USER_ACTIONS:
- Interactuar con medium_region around [45,79]
- Interactuar con medium_region around [67,34]
- Interactuar con medium_region around [34,36]
- Interactuar con tiny_region around [92,30]
- Interactuar con tiny_region around [31,88]

UNCERTAINTIES:
- La detección de objetos tiene precisión limitada (20 regiones detectadas)

DO_NOT_ASSUME:
- No asumir texto legible donde OCR no lo confirmó
- No asumir funcionalidad de elementos no etiquetados
- No asumir contenido fuera del área visible

FINAL_INTERPRETATION_FOR_TEXT_ONLY_AI:
- Imagen de 1024x1536 píxeles. Tono mixto. Contiene texto legible. Complejidad alta con 20 elementos detectados.
- Zona principal: medium_region
- Contiene texto: [text_zone] | [text_zone] | [text_zone] | [text_zone] | [text_zone]
- Tonalidad: mixto
