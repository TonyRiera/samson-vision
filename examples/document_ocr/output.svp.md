[SAMSON_VISION_PACK v1]

IMAGE_TYPE:
- domain: web
- subtype: generic
- quality: medium
- dimensions: 682x1024
- aspect_ratio: 0.666

GLOBAL_SUMMARY:
- La imagen contiene 6 regiones visuales detectadas. Tonalidad general: mixto. La imagen tiene complejidad visual alta. Se detectaron 5 zonas de texto. Nivel 1 (PRINCIPAL): 1 elementos. Nivel 3 (DETALLE): 5 elementos.

VISUAL_HIERARCHY:
- [0,2,100,100] large_region (nivel 1)
- [37,0,60,6] tiny_region (nivel 3)
- [89,17,96,22] tiny_region (nivel 3)
- [65,77,70,83] tiny_region (nivel 3)
- [50,89,56,93] tiny_region (nivel 3)
- [19,92,26,96] tiny_region (nivel 3)

LAYOUT_MAP:
- [0,2,100,100] large_region
- [37,0,60,6] tiny_region
- [89,17,96,22] tiny_region
- [65,77,70,83] tiny_region
- [50,89,56,93] tiny_region
- [19,92,26,96] tiny_region

OCR_TEXT:
- "[text_zone]" at [60,10,70,20], confidence medium
- "[text_zone]" at [70,40,80,50], confidence medium
- "[text_zone]" at [10,60,20,80], confidence medium
- "[text_zone]" at [40,60,60,70], confidence medium
- "[text_zone]" at [40,80,60,90], confidence medium

OBJECTS_AND_COMPONENTS:
- large_region at [0,2,100,100], area 98%
- tiny_region at [37,0,60,6], area 1%
- tiny_region at [89,17,96,22], area 0%
- tiny_region at [65,77,70,83], area 0%
- tiny_region at [50,89,56,93], area 0%
- tiny_region at [19,92,26,96], area 0%

COLOR_MAP:
- gray_dark: 26%
- black: 26%
- gray_dark: 21%
- brown_medium: 14%
- gray_medium: 3%
- red_medium: 3%

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
@@@@@@@@@@@@@@%%%%%%%%%%%%%%%%##***++=-::::-:::... ...:-=+++*###%%%@@@@@@@@@@@@@
@@@@@@@@@@@@%%%%%%##########**++-:::::::::...::......:--===+****###%%%%%%@@@@@@@
@@@@@@@@@@@@%%###*********++++===-------:.:--:::..:::-===++==-::=+**#####%%%@@@@
@@@@@@@%%%%####*********++++++======---:..:--::::::--===+==-::-=++****###%%%%%@@
@@@@%%%######%%%%%%###%##+*###*****+++======-======-=======-:-=++***#####%%%%%%%
@@%%%%%%%%%%%%%%%%####%%##%%%*+*+=++++**++++++******###++====+****#*+***+++*#%%%
```

USER_ACTIONS:
- Interactuar con large_region around [50,51]
- Interactuar con tiny_region around [49,3]
- Interactuar con tiny_region around [92,20]
- Interactuar con tiny_region around [67,80]
- Interactuar con tiny_region around [53,91]

UNCERTAINTIES:
- La detección de objetos tiene precisión limitada (6 regiones detectadas)

DO_NOT_ASSUME:
- No asumir texto legible donde OCR no lo confirmó
- No asumir funcionalidad de elementos no etiquetados
- No asumir contenido fuera del área visible

FINAL_INTERPRETATION_FOR_TEXT_ONLY_AI:
- Imagen de 682x1024 píxeles. Tono mixto. Contiene texto legible. Complejidad alta con 6 elementos detectados.
- Zona principal: large_region
- Contiene texto: [text_zone] | [text_zone] | [text_zone] | [text_zone] | [text_zone]
- Tonalidad: mixto
