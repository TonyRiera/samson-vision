[SAMSON_VISION_PACK v1]

IMAGE_TYPE:
- domain: web
- subtype: generic
- quality: medium
- dimensions: 1536x1024
- aspect_ratio: 1.5

GLOBAL_SUMMARY:
- La imagen contiene 19 regiones visuales detectadas. Tonalidad general: oscuro/neutro. La imagen tiene complejidad visual alta. Se detectaron 15 zonas de texto. Nivel 1 (PRINCIPAL): 1 elementos. Nivel 3 (DETALLE): 18 elementos.

VISUAL_HIERARCHY:
- [0,0,100,100] large_region (nivel 1)
- [8,30,17,43] tiny_region (nivel 3)
- [13,83,22,94] tiny_region (nivel 3)
- [97,2,100,18] tiny_region (nivel 3)
- [0,16,4,26] tiny_region (nivel 3)
- [13,20,18,26] tiny_region (nivel 3)
- [89,92,97,96] tiny_region (nivel 3)
- [2,5,5,14] tiny_region (nivel 3)
- [84,80,88,87] tiny_region (nivel 3)
- [11,29,15,36] tiny_region (nivel 3)

LAYOUT_MAP:
- [0,0,100,100] large_region
- [8,30,17,43] tiny_region
- [13,83,22,94] tiny_region
- [97,2,100,18] tiny_region
- [0,16,4,26] tiny_region
- [13,20,18,26] tiny_region
- [89,92,97,96] tiny_region
- [2,5,5,14] tiny_region
- [84,80,88,87] tiny_region
- [11,29,15,36] tiny_region
- [2,95,7,100] tiny_region
- [0,26,2,38] tiny_region
- [43,98,56,100] tiny_region
- [83,0,85,5] tiny_region
- [40,0,45,2] tiny_region

OCR_TEXT:
- "[text_zone]" at [40,0,50,10], confidence medium
- "[text_zone]" at [30,10,50,30], confidence medium
- "[text_zone]" at [60,10,80,30], confidence medium
- "[text_zone]" at [50,20,60,30], confidence medium
- "[text_zone]" at [20,30,40,50], confidence medium
- "[text_zone]" at [80,30,90,50], confidence high
- "[text_zone]" at [50,40,80,60], confidence medium
- "[text_zone]" at [20,50,40,70], confidence medium
- "[text_zone]" at [50,50,80,70], confidence medium
- "[text_zone]" at [20,60,40,80], confidence medium
- "[text_zone]" at [0,70,30,80], confidence medium
- "[text_zone]" at [60,70,80,90], confidence medium
- "[text_zone]" at [80,70,100,80], confidence medium
- "[text_zone]" at [40,90,60,100], confidence high
- "[text_zone]" at [60,90,70,100], confidence high

OBJECTS_AND_COMPONENTS:
- large_region at [0,0,100,100], area 100%
- tiny_region at [8,30,17,43], area 1%
- tiny_region at [13,83,22,94], area 1%
- tiny_region at [97,2,100,18], area 0%
- tiny_region at [0,16,4,26], area 0%
- tiny_region at [13,20,18,26], area 0%
- tiny_region at [89,92,97,96], area 0%
- tiny_region at [2,5,5,14], area 0%
- tiny_region at [84,80,88,87], area 0%
- tiny_region at [11,29,15,36], area 0%
- tiny_region at [2,95,7,100], area 0%
- tiny_region at [0,26,2,38], area 0%
- tiny_region at [43,98,56,100], area 0%
- tiny_region at [83,0,85,5], area 0%
- tiny_region at [40,0,45,2], area 0%

COLOR_MAP:
- black: 35%
- gray_dark: 18%
- gray_dark: 11%
- gray_medium: 11%
- gray_medium: 5%
- gray_dark: 4%

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
%%@@@%%######%@@@@@@@@%@@%%%@@@@%%@@@@@@@@@@@@%%@@@%@@@@%%%%%@@@@@%#%%%%%%%@@@%%
%@@@@%#%%%%%%%@@@@@@%#+%%%##%####**###**#######%%%%%%%%%%%%%%%%@@@%%%@@%%#%%%@%%
%@@%@%%@@@@@@@%%%##@%##%%##*+++++==+*++++***##%%@@@%##%%%#%#%%%#@@@@@@@@%#%%#@%%
%@@@%#%@@@@@@@@%%*+%#+#%#**++*####**##****##%%%@@@@%*####*%**#*#@@@@@@%%%%#%%%@%
@@@@##%%%@%%%%%%%+=##%%%#++=+%@@@@@@@@%%%%@@@@@@@@@@*=-+#%%%%%++%%%%%%%%%##%@%@@
@@@@%#%@%%@%%@@@%##@%%%%%*-+######%########%%#%%%%%%%=+#######**%%%%%%%###%%%%@@
```

USER_ACTIONS:
- Interactuar con large_region around [50,50]
- Interactuar con tiny_region around [13,36]
- Interactuar con tiny_region around [17,89]
- Interactuar con tiny_region around [98,10]
- Interactuar con tiny_region around [2,21]

UNCERTAINTIES:
- La detección de objetos tiene precisión limitada (19 regiones detectadas)

DO_NOT_ASSUME:
- No asumir texto legible donde OCR no lo confirmó
- No asumir funcionalidad de elementos no etiquetados
- No asumir contenido fuera del área visible

FINAL_INTERPRETATION_FOR_TEXT_ONLY_AI:
- Imagen de 1536x1024 píxeles. Tono oscuro/neutro. Contiene texto legible. Complejidad alta con 19 elementos detectados.
- Zona principal: large_region
- Contiene texto: [text_zone] | [text_zone] | [text_zone] | [text_zone] | [text_zone]
- Tonalidad: oscuro/neutro
