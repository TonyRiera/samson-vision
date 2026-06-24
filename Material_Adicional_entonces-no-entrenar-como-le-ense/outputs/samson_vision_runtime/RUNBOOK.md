# Runbook

## Crear prompt para una imagen web

Preparar Python:

```powershell
$PY="C:\Users\antonio\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
```

```powershell
& $PY .\outputs\samson_vision_runtime\scripts\samson_vision_runtime.py build-prompt --domain web --mode agent_action --out .\outputs\samson_vision_runtime\prompt_web_agent_action.generated.md
```

Enviar ese prompt y la imagen al modelo con visión.

## Validar salida

```powershell
& $PY .\outputs\samson_vision_runtime\scripts\validate_pack.py .\pack_generado.md
```

Si devuelve `VALID: false`, pedir corrección:

```text
Usa prompts/correction_prompt.md y corrige solo lo necesario.
```

## Enviar a DeepSeek / Nous / texto

```powershell
& $PY .\outputs\samson_vision_runtime\scripts\demo_text_only_model.py .\pack_generado.md --question "Qué debe hacer el agente ahora?"
```

## Probar todo el sistema

```powershell
& $PY .\outputs\samson_vision_runtime\scripts\smoke_test.py
```

## Añadir aprendizaje externo

Cuando haya un fallo real:

1. Añadir el caso a `memory/05_COMMON_ERRORS.md`.
2. Crear ejemplo malo en `examples/bad`.
3. Crear ejemplo corregido en `examples/good` si aplica.
4. Añadir metadatos en `rag_index.jsonl`.
5. Probar que el prompt recupera el nuevo patrón.
