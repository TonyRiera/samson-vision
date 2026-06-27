# Samson Vision Runtime

Sistema para que un modelo con visión actúe como lazarillo de DeepSeek v4 Flash, Nous Agent o cualquier modelo sin visión, sin entrenar pesos.

La idea es envolver al modelo con:

- `harness`: contrato obligatorio de trabajo.
- `knowledge`: RAG local con reglas, patrones y ejemplos.
- `schemas`: formato verificable del paquete visual.
- `examples`: salidas buenas/malas para few-shot y validación.
- `scripts`: runtime mínimo para recuperar contexto, construir prompts y validar salidas.
- `memory`: aprendizaje externo de errores y mejoras.
- `subagents`: prompts concretos para montar el flujo en Nous Agent.
- `templates`: plantilla vacía del pack para integraciones.

## Flujo

```text
Imagen / captura / web / Excel / dashboard
        ↓
OCR / DOM / color / layout / visión
        ↓
Samson Vision Runtime recupera reglas RAG
        ↓
Modelo con visión genera SAMSON_VISION_PACK
        ↓
Validador detecta omisiones o alucinaciones
        ↓
DeepSeek / Nous / modelo texto razona con el pack
```

## Uso rápido

Si `python` no está en `PATH` en esta máquina, usa el Python embebido de Codex:

```powershell
$PY=python3
```

Generar un prompt listo para un modelo con visión:

```powershell
& $PY .\outputs\samson_vision_runtime\scripts\samson_vision_runtime.py build-prompt --domain web --mode agent_action
```

Validar un pack generado:

```powershell
& $PY .\outputs\samson_vision_runtime\scripts\validate_pack.py .\outputs\samson_vision_runtime\examples\good\web_google_home_pack.md
```

Crear el prompt para DeepSeek o cualquier modelo sin visión:

```powershell
& $PY .\outputs\samson_vision_runtime\scripts\demo_text_only_model.py .\outputs\samson_vision_runtime\examples\good\web_google_home_pack.md
```

Prueba completa del sistema:

```powershell
& $PY .\outputs\samson_vision_runtime\scripts\smoke_test.py
```

## Modos

- `fast`: resumen, OCR y layout mínimo.
- `standard`: pack completo.
- `deep`: pack completo, ASCII, incertidumbres y validación estricta.
- `agent_action`: orientado a acciones: dónde mirar, clicar, evitar o pedir zoom.

## Integración con Nous Agent

Usa estos subagentes:

- `vision_scout`: llama al modelo con visión.
- `ocr_agent`: extrae texto con coordenadas.
- `layout_agent`: organiza zonas.
- `rag_retriever`: trae reglas y ejemplos.
- `pack_writer`: fuerza el esquema `SAMSON_VISION_PACK`.
- `validator_agent`: revisa fidelidad.
- `text_reasoner`: pasa el pack a DeepSeek / Nous / modelo texto.

El modelo sin visión nunca recibe la imagen: recibe un paquete textual fiel, con coordenadas, OCR, incertidumbre y límites explícitos.

Consulta `NOUS_AGENT_BLUEPRINT.md` y `subagents/` para copiar los contratos directamente.
