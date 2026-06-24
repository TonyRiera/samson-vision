# 06 — Excel Patterns

Recuperar cuando `domain=excel` o `spreadsheet`.

Prioridades:

1. Nombre de hoja si visible.
2. Rango visible de filas y columnas.
3. Celda activa y selección.
4. Encabezados, filtros y celdas resaltadas.
5. Fórmula visible en la barra de fórmulas.
6. Tablas y gráficos.

Acciones:

- Expresar celdas como coordenadas visuales y, si es legible, como referencias tipo `B3`.
- Distinguir valor visible de fórmula.
- Marcar texto truncado o celdas ocultas.

Errores comunes:

- Inferir columnas fuera del recorte.
- Afirmar fórmulas cuando solo se ve un valor.
- Ignorar filtros activos.

