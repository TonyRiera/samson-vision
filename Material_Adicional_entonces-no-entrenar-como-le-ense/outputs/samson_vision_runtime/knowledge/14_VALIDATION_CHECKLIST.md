# 14 — Validation Checklist

El validador debe revisar:

1. Tiene encabezado `[SAMSON_VISION_PACK v1]`.
2. Incluye todos los campos obligatorios.
3. Tiene coordenadas normalizadas en layout u objetos.
4. Separa OCR de interpretación.
5. Incluye incertidumbres.
6. Incluye `DO_NOT_ASSUME`.
7. Incluye acciones o explica que no hay acciones.
8. No afirma texto con baja legibilidad como hecho seguro.
9. No inventa elementos fuera del recorte.
10. Sirve para una IA sin visión.

Si falla, pedir corrección con:

```text
Corrige la salida anterior.
No añadas contenido inventado.
Añade coordenadas faltantes.
Añade incertidumbres donde corresponda.
Respeta SAMSON_VISION_PACK v1.
```

