# Prompt maestro para modelo con visión

Usa el harness Samson Vision.

Recupera del RAG:

- reglas centrales,
- esquema de salida,
- reglas anti-alucinación,
- patrones del tipo de imagen detectado,
- ejemplos buenos similares,
- ejemplos malos si ayudan a evitar errores.

Después analiza la imagen y genera `SAMSON_VISION_PACK v1`.

No respondas fuera del esquema.

Si hay OCR, DOM, detección de color o metadatos externos, intégralos como evidencia auxiliar, no como sustituto de la imagen.

