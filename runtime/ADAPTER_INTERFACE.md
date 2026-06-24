# Adapter Interface

Este runtime no depende de un proveedor concreto. Cualquier modelo con visión puede enchufarse si acepta un prompt y una imagen, y devuelve texto.

## Contrato mínimo

```python
class VisionModelAdapter:
    def analyze(self, image_path: str, prompt: str, tool_context: dict | None = None) -> str:
        """Return a SAMSON_VISION_PACK v1 Markdown string."""
```

## Contexto opcional de herramientas

```json
{
  "ocr": [
    {"text": "Aceptar", "box": [60, 54, 68, 58], "confidence": "high"}
  ],
  "dom": {
    "url": "https://example.com",
    "visible_buttons": ["Login", "Search"]
  },
  "image_stats": {
    "width": 1920,
    "height": 1080,
    "dominant_colors": ["white", "gray_light", "blue_medium"]
  }
}
```

## Ciclo recomendado

1. `build-prompt` con dominio y modo.
2. Llamar al modelo con visión.
3. Validar con `validate_pack.py`.
4. Si falla, aplicar `prompts/correction_prompt.md`.
5. Enviar pack validado al modelo sin visión.

## Política de seguridad

El modelo texto no debe ejecutar acciones en pantalla si:

- El pack no valida.
- La acción no tiene coordenadas.
- El elemento está marcado con confianza baja.
- Hay un modal bloqueante no resuelto.
- `DO_NOT_ASSUME` contradice la acción.

