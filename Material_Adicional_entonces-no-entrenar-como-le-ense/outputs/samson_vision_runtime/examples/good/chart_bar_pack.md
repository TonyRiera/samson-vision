[SAMSON_VISION_PACK v1]

IMAGE_TYPE:
- domain: chart
- subtype: bar chart
- quality: medium
- crop: complete

GLOBAL_SUMMARY:
- Gráfico de barras con varias categorías en el eje horizontal y una escala numérica vertical parcialmente legible.

VISUAL_HIERARCHY:
- [10,8,90,18] título.
- [12,22,88,78] área del gráfico.
- [12,78,88,88] etiquetas de categorías.
- [2,22,12,78] eje vertical.

LAYOUT_MAP:
- [10,8,90,18] title_area.
- [12,22,88,78] plot_area.
- [2,22,12,78] y_axis.
- [12,78,88,88] x_axis_labels.

OCR_TEXT:
- "Ventas por región" at [20,9,58,15], confidence high.
- Algunas etiquetas del eje X at [15,80,85,86], confidence medium.
- Números del eje Y at [4,24,10,74], confidence low.

OBJECTS_AND_COMPONENTS:
- bar_series at [18,35,82,78], multiple vertical bars.
- y_axis at [10,22,10,78], scale partially visible.
- x_axis at [12,78,88,78].

COLOR_MAP:
- bars: blue_medium.
- background: white.
- grid: gray_light.
- text: gray_dark.

DENSITY_MAP:
- Plot area medium density.
- Labels lower area medium density.
- Margins low density.

ASCII_REPRESENTATION:
```text
+------------------------------------------------+
| Ventas por región                              |
|     |        █                                 |
|     |   █    █        █                        |
|     |   █    █   █    █                        |
|     +--------------------------------          |
|        cat1 cat2 cat3 cat4                     |
+------------------------------------------------+
```

USER_ACTIONS:
- Use the chart for qualitative comparison only unless OCR/zoom confirms y-axis values.
- Request zoom on [2,22,12,78] for exact scale.

UNCERTAINTIES:
- Exact y-axis values are low confidence.
- Some x-axis labels are partially legible.

DO_NOT_ASSUME:
- Do not invent exact numeric values.
- Do not infer cause of differences.
- Do not assume missing categories outside the crop.

FINAL_INTERPRETATION_FOR_TEXT_ONLY_AI:
- The chart supports relative visual comparison between bars, but exact values require better OCR or zoom.

