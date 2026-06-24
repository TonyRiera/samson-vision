[SAMSON_VISION_PACK v1]

IMAGE_TYPE:
- domain: web
- subtype: search homepage
- quality: high
- crop: complete

GLOBAL_SUMMARY:
- Página inicial de buscador con logo central, barra de búsqueda, dos botones principales y enlaces superiores/inferiores.

VISUAL_HIERARCHY:
- [38,28,62,38] logo central del buscador.
- [26,43,74,50] campo de búsqueda.
- [35,54,65,61] dos botones bajo el campo.
- [0,0,100,8] navegación superior.
- [0,90,100,100] footer.

LAYOUT_MAP:
- [0,0,100,8] header con enlaces y acceso.
- [0,8,100,90] área principal blanca.
- [26,43,74,50] campo de búsqueda centrado.
- [35,54,65,61] fila de botones.
- [0,90,100,100] footer gris claro.

OCR_TEXT:
- "Buscar con Google" at [36,55,48,59], confidence high.
- "Voy a tener suerte" at [50,55,65,59], confidence high.
- "Iniciar sesión" at [86,2,98,7], confidence medium.

OBJECTS_AND_COMPONENTS:
- search_input at [26,43,74,50], rounded rectangle, empty.
- button at [35,54,49,61], text "Buscar con Google".
- button at [51,54,65,61], text "Voy a tener suerte".
- login_button_or_link at [86,2,98,7], text confidence medium.

COLOR_MAP:
- background: white.
- footer: gray_light.
- buttons: gray_very_light.
- primary text: gray_dark/black.

DENSITY_MAP:
- Top header low density.
- Center medium density around logo/search/buttons.
- Footer medium density with small links.

ASCII_REPRESENTATION:
```text
+------------------------------------------------+
| links                             [Iniciar]    |
|                                                |
|                    LOGO                        |
|              [ search input ]                  |
|        [Buscar] [Voy a tener suerte]           |
|                                                |
| footer links                                   |
+------------------------------------------------+
```

USER_ACTIONS:
- Click search input around [50,46].
- Click first button around [42,57].
- Click second button around [58,57].
- Click login/access link around [92,5] if needed.

UNCERTAINTIES:
- Texto exacto del enlace superior derecho tiene confianza media por tamaño.

DO_NOT_ASSUME:
- No asumir resultados de búsqueda.
- No asumir anuncios.
- No asumir menú lateral.

FINAL_INTERPRETATION_FOR_TEXT_ONLY_AI:
- La imagen muestra una página inicial de buscador lista para introducir una consulta; no hay resultados todavía. Las acciones seguras son escribir en la barra central o pulsar uno de los dos botones visibles.

