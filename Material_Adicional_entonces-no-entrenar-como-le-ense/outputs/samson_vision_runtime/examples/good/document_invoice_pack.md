[SAMSON_VISION_PACK v1]

IMAGE_TYPE:
- domain: document
- subtype: invoice or business document
- quality: medium
- crop: partial

GLOBAL_SUMMARY:
- Documento tipo factura con título superior, datos de emisor/receptor, tabla central de líneas y total en la zona inferior derecha.

VISUAL_HIERARCHY:
- [5,4,45,12] título y encabezado.
- [5,14,45,28] bloque de datos izquierdo.
- [55,14,95,28] bloque de datos derecho.
- [5,32,95,72] tabla de conceptos.
- [62,76,95,90] totales.

LAYOUT_MAP:
- [0,0,100,100] página blanca del documento.
- [5,4,95,12] header.
- [5,32,95,72] line_items_table.
- [62,76,95,90] totals_box.

OCR_TEXT:
- "FACTURA" at [5,5,25,10], confidence high.
- "Total" at [70,80,82,85], confidence high.
- Texto de líneas de tabla at [8,38,90,68], confidence low.

OBJECTS_AND_COMPONENTS:
- document_title at [5,4,45,12], text "FACTURA".
- table at [5,32,95,72], multiple rows.
- totals_box at [62,76,95,90], summary amounts.

COLOR_MAP:
- background: white.
- text: black/gray_dark.
- table_lines: gray_light.

DENSITY_MAP:
- Header medium density.
- Table high density.
- Margins low density.

ASCII_REPRESENTATION:
```text
+------------------------------------------------+
| FACTURA                                        |
| Sender block                 Client/date block |
|                                                |
| Item table: description | qty | price | total  |
| ...                                            |
|                              subtotal / total  |
+------------------------------------------------+
```

USER_ACTIONS:
- Request zoom/OCR for table rows at [5,32,95,72] before extracting amounts.
- Inspect total box at [62,76,95,90] if the task asks for payment amount.

UNCERTAINTIES:
- Exact table line text is low confidence.
- Currency symbol is not reliably legible.

DO_NOT_ASSUME:
- Do not assume tax rate.
- Do not assume invoice number if not legible.
- Do not invent table line amounts.

FINAL_INTERPRETATION_FOR_TEXT_ONLY_AI:
- The image is a business document/factura layout. The structure is clear, but exact financial values require OCR or zoom before reasoning.

