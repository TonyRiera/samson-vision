[SAMSON_VISION_PACK v1]

IMAGE_TYPE:
- domain: web
- subtype: generic
- quality: medium
- dimensions: 682x1024
- aspect_ratio: 0.666

GLOBAL_SUMMARY:
- La imagen contiene 10 regiones visuales detectadas. Tonalidad general: mixto. La imagen tiene complejidad visual media. Se detectaron 8 zonas de texto. Nivel 1 (PRINCIPAL): 2 elementos. Nivel 2 (SECUNDARIO): 1 elementos. Nivel 3 (DETALLE): 7 elementos.

VISUAL_HIERARCHY:
- [0,18,100,100] large_region (nivel 1)
- [44,0,92,33] medium_region (nivel 1)
- [5,9,41,26] small_region (nivel 2)
- [0,51,18,67] tiny_region (nivel 3)
- [8,0,29,7] tiny_region (nivel 3)
- [62,15,77,22] tiny_region (nivel 3)
- [52,44,61,55] tiny_region (nivel 3)
- [37,73,54,79] tiny_region (nivel 3)
- [42,67,52,74] tiny_region (nivel 3)
- [88,0,94,2] tiny_region (nivel 3)

LAYOUT_MAP:
- [0,18,100,100] large_region
- [44,0,92,33] medium_region
- [5,9,41,26] small_region
- [0,51,18,67] tiny_region
- [8,0,29,7] tiny_region
- [62,15,77,22] tiny_region
- [52,44,61,55] tiny_region
- [37,73,54,79] tiny_region
- [42,67,52,74] tiny_region
- [88,0,94,2] tiny_region

OCR_TEXT:
- "[text_zone]" at [40,0,60,10], confidence high
- "[text_zone]" at [40,30,70,50], confidence high
- "[text_zone]" at [30,40,40,50], confidence medium
- "[text_zone]" at [30,50,40,60], confidence medium
- "[text_zone]" at [60,50,80,60], confidence high
- "[text_zone]" at [20,60,30,70], confidence high
- "[text_zone]" at [20,80,40,90], confidence medium
- "[text_zone]" at [50,80,70,100], confidence high

OBJECTS_AND_COMPONENTS:
- large_region at [0,18,100,100], area 82%
- medium_region at [44,0,92,33], area 16%
- small_region at [5,9,41,26], area 6%
- tiny_region at [0,51,18,67], area 3%
- tiny_region at [8,0,29,7], area 1%
- tiny_region at [62,15,77,22], area 1%
- tiny_region at [52,44,61,55], area 1%
- tiny_region at [37,73,54,79], area 1%
- tiny_region at [42,67,52,74], area 1%
- tiny_region at [88,0,94,2], area 0%

COLOR_MAP:
- black: 34%
- gray_dark: 17%
- brown_medium: 13%
- gray_dark: 12%
- red_medium: 8%
- gray_light: 5%

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
@@@@@%%##%###**=::=+****++=-::...... ..::------===+**++++++++****###*##*###%%@@@
@@@@@@@@%%%%%###++++=++++==-::.....:-+***#**++*##**#%%**#####%%%%%%%%%%%%%%%@@@@
@@@@@@%%%%%#####%#####**+==-::......-+#%#%%%*++=---=****#####%%%%%%%%%%%%%%%%%%%
@@@@@%%%%#*###***++*+++++==-::::......:--==---:...:-=+++**##*****#########%%%%%%
@@@@@@@%%%%%%%#####*++++==---:::::::.:..::..::::::::::--==----:--=++*###%%%@@@@@
@@@@@@@@@@@@@@%%%%%%##*+==++=-----:::::::::::---:---------==+++++++*###%%%%@@@@@
```

USER_ACTIONS:
- Interactuar con large_region around [50,59]
- Interactuar con medium_region around [68,17]
- Interactuar con small_region around [23,18]
- Interactuar con tiny_region around [9,59]
- Interactuar con tiny_region around [19,3]

UNCERTAINTIES:
- La detección de objetos tiene precisión limitada (10 regiones detectadas)

DO_NOT_ASSUME:
- No asumir texto legible donde OCR no lo confirmó
- No asumir funcionalidad de elementos no etiquetados
- No asumir contenido fuera del área visible

FINAL_INTERPRETATION_FOR_TEXT_ONLY_AI:
- Imagen de 682x1024 píxeles. Tono mixto. Contiene texto legible. Complejidad media con 10 elementos detectados.
- Zona principal: large_region, medium_region
- Zonas secundarias: small_region
- Contiene texto: [text_zone] | [text_zone] | [text_zone] | [text_zone] | [text_zone]
