[SAMSON_VISION_PACK v1]

IMAGE_TYPE:
- domain: dashboard
- subtype: KPI dashboard
- quality: medium
- crop: complete

GLOBAL_SUMMARY:
- Dashboard con barra lateral, tarjetas KPI superiores, gráfico central y tabla inferior.

VISUAL_HIERARCHY:
- [0,0,18,100] sidebar.
- [20,8,95,24] fila de KPI cards.
- [20,28,70,68] gráfico principal.
- [72,28,95,68] panel secundario.
- [20,72,95,96] tabla inferior.

LAYOUT_MAP:
- [0,0,18,100] sidebar navigation.
- [18,0,100,8] top bar.
- [20,8,95,24] KPI cards.
- [20,28,70,68] chart area.
- [72,28,95,68] status panel.
- [20,72,95,96] data table.

OCR_TEXT:
- "Revenue" at [22,10,34,14], confidence high.
- "Orders" at [42,10,52,14], confidence high.
- "Conversion" at [62,10,76,14], confidence medium.
- "Status" at [74,30,84,34], confidence high.

OBJECTS_AND_COMPONENTS:
- kpi_card at [20,8,38,24], label Revenue.
- kpi_card at [40,8,58,24], label Orders.
- kpi_card at [60,8,78,24], label Conversion.
- line_chart at [20,28,70,68], upward trend visually apparent.
- table at [20,72,95,96].

COLOR_MAP:
- sidebar: blue_dark.
- cards: white.
- positive accents: green_medium.
- warnings: orange/yellow in status panel.

DENSITY_MAP:
- Sidebar medium density.
- KPI row low density.
- Chart medium density.
- Table high density.

ASCII_REPRESENTATION:
```text
+-----+------------------------------------------+
| nav | top bar                                  |
|     | [Revenue] [Orders] [Conversion]          |
|     |                                          |
|     |       line chart          status panel   |
|     |                                          |
|     |              table rows                  |
+-----+------------------------------------------+
```

USER_ACTIONS:
- Inspect KPI cards first.
- For exact numbers, request OCR/zoom on [20,8,78,24].
- For trend reasoning, use chart as qualitative unless axis labels are legible.

UNCERTAINTIES:
- Exact KPI numeric values are not reliably legible.
- Trend appears upward but precise slope is not measurable.

DO_NOT_ASSUME:
- Do not infer business cause from trend.
- Do not invent exact chart values.
- Do not assume filters not visible.

FINAL_INTERPRETATION_FOR_TEXT_ONLY_AI:
- The dashboard shows business metrics with KPI cards, a main trend chart and a data table. It supports high-level visual reasoning, but exact numeric claims need OCR or zoom.

