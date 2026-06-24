[SAMSON_VISION_PACK v1]

IMAGE_TYPE:
- domain: excel
- subtype: spreadsheet table
- quality: medium
- crop: partial

GLOBAL_SUMMARY:
- Hoja de cálculo con una tabla de ventas visible, encabezados en la fila superior y una celda seleccionada dentro del rango.

VISUAL_HIERARCHY:
- [0,0,100,15] cinta/barra superior.
- [0,15,100,22] barra de fórmulas y nombres.
- [6,23,95,88] cuadrícula con tabla.
- [18,31,78,62] rango principal de datos.

LAYOUT_MAP:
- [0,0,100,15] ribbon parcialmente visible.
- [0,15,100,22] formula_bar.
- [0,22,6,88] row_numbers.
- [6,22,95,27] column_headers.
- [6,27,95,88] grid_area.

OCR_TEXT:
- "Producto" at [8,28,20,32], confidence high.
- "Ventas" at [32,28,42,32], confidence high.
- "Región" at [48,28,58,32], confidence medium.
- "Total" at [66,28,74,32], confidence high.

OBJECTS_AND_COMPONENTS:
- table_header at [6,27,78,33], highlighted row.
- active_cell at [32,40,42,46], border visible.
- grid_cells at [6,27,95,88], spreadsheet grid.

COLOR_MAP:
- grid background: white.
- header row: blue_light.
- active cell border: green_medium.
- text: black.

DENSITY_MAP:
- Ribbon high density.
- Table region medium density.
- Lower grid sparse.

ASCII_REPRESENTATION:
```text
+------------------------------------------------+
| Ribbon / toolbar                               |
| Formula bar                                    |
|    A Producto | B Ventas | C Región | D Total  |
| 1  ...        | ...      | ...      | ...      |
| 2  ...        | [active] | ...      | ...      |
+------------------------------------------------+
```

USER_ACTIONS:
- Read table headers before reasoning about columns.
- If formula is needed, request zoom on formula bar because formula text is not visible enough.
- Active cell can be referenced visually around [37,43].

UNCERTAINTIES:
- Exact contents of most cells are not legible.
- Sheet tab name is not visible in crop.

DO_NOT_ASSUME:
- Do not assume formulas.
- Do not infer hidden rows or columns.
- Do not assume totals are correct.

FINAL_INTERPRETATION_FOR_TEXT_ONLY_AI:
- This is a partial spreadsheet view. The visible reliable facts are the table structure, some headers and the active cell location; detailed values require OCR/zoom.

