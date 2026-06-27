[SAMSON_VISION_PACK v1]

IMAGE_TYPE:
- domain: web
- subtype: generic
- quality: medium
- dimensions: 1024x1536
- aspect_ratio: 0.667

GLOBAL_SUMMARY:
- La imagen contiene 20 regiones visuales detectadas. Tonalidad general: mixto. La imagen tiene complejidad visual media. Se detectaron 1 zonas de texto. Nivel 1 (PRINCIPAL): 1 elementos. Nivel 2 (SECUNDARIO): 1 elementos. Nivel 3 (DETALLE): 18 elementos.

VISUAL_HIERARCHY:
- [0,11,100,98] large_region (nivel 1)
- [78,1,100,38] small_region (nivel 2)
- [26,1,42,22] small_region (nivel 3)
- [54,0,65,13] tiny_region (nivel 3)
- [84,2,96,12] tiny_region (nivel 3)
- [10,3,22,12] tiny_region (nivel 3)
- [40,95,51,100] tiny_region (nivel 3)
- [41,0,48,7] tiny_region (nivel 3)
- [29,0,41,3] tiny_region (nivel 3)
- [60,92,68,96] tiny_region (nivel 3)

LAYOUT_MAP:
- [0,11,100,98] large_region
- [78,1,100,38] small_region
- [26,1,42,22] small_region
- [54,0,65,13] tiny_region
- [84,2,96,12] tiny_region
- [10,3,22,12] tiny_region
- [40,95,51,100] tiny_region
- [41,0,48,7] tiny_region
- [29,0,41,3] tiny_region
- [60,92,68,96] tiny_region
- [2,2,4,13] tiny_region
- [10,21,15,27] tiny_region
- [44,6,50,9] tiny_region
- [71,24,78,27] tiny_region
- [37,98,47,100] tiny_region

OCR_TEXT:
- "[text_zone]" at [50,20,60,30], confidence medium

OBJECTS_AND_COMPONENTS:
- large_region at [0,11,100,98], area 87%
- small_region at [78,1,100,38], area 8%
- small_region at [26,1,42,22], area 3%
- tiny_region at [54,0,65,13], area 2%
- tiny_region at [84,2,96,12], area 1%
- tiny_region at [10,3,22,12], area 1%
- tiny_region at [40,95,51,100], area 0%
- tiny_region at [41,0,48,7], area 0%
- tiny_region at [29,0,41,3], area 0%
- tiny_region at [60,92,68,96], area 0%
- tiny_region at [2,2,4,13], area 0%
- tiny_region at [10,21,15,27], area 0%
- tiny_region at [44,6,50,9], area 0%
- tiny_region at [71,24,78,27], area 0%
- tiny_region at [37,98,47,100], area 0%

COLOR_MAP:
- black: 30%
- gray_dark: 25%
- brown_medium: 14%
- gray_dark: 10%
- gray_medium: 5%
- red_medium: 4%

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
@@@@@@@@@@@%%%%%%%%####**+=---------::.. .:---::---===+****####%%%%@@@@%%@@@@@@@
@@@@@@@%%%%%############**++++====---::..:::--=---==++******###%%%%%%%%%#%%%@@@@
@@@@%%%%%%#%%#######**+++====---::::::....::::----==++**++++*##%%%%%%%%%%%%%@@@@
@@@@@%%%%%%#########***++====-----::--::.::::::-----=======+***#######%%%%%%@@@@
@@@@%%%%%%%%####********+=======-===---:.::----========++*+++***#######%%%%%%%%@
@@@%%%%%%%#######*****++++=====-------:..::--::--==+=+==++****#######%%%%%%%%@@@
```

USER_ACTIONS:
- Interactuar con large_region around [50,55]
- Interactuar con small_region around [89,19]
- Interactuar con small_region around [34,11]
- Interactuar con tiny_region around [59,6]
- Interactuar con tiny_region around [90,7]

UNCERTAINTIES:
- La detección de objetos tiene precisión limitada (20 regiones detectadas)

DO_NOT_ASSUME:
- No asumir texto legible donde OCR no lo confirmó
- No asumir funcionalidad de elementos no etiquetados
- No asumir contenido fuera del área visible

FINAL_INTERPRETATION_FOR_TEXT_ONLY_AI:
- Imagen de 1024x1536 píxeles. Tono mixto. Contiene texto legible. Complejidad media con 20 elementos detectados.
- Zona principal: large_region
- Zonas secundarias: small_region
- Contiene texto: [text_zone]
