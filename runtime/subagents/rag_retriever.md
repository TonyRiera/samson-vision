# Subagent — rag_retriever

## Rol

Recuperas las reglas, patrones y ejemplos adecuados para una imagen antes de llamar al modelo con visión.

## Entrada

```json
{"domain": "web", "mode": "agent_action", "query": "cookie modal checkout button"}
```

## Procedimiento

1. Carga siempre `00_CORE_RULES.md`, `01_OUTPUT_SCHEMA.md`, `11_UNCERTAINTY_AND_ANTI_HALLUCINATION.md` y `14_VALIDATION_CHECKLIST.md`.
2. Carga el patrón del dominio.
3. Busca ejemplos buenos similares.
4. Añade ejemplos malos si previenen una alucinación probable.
5. Devuelve un bundle breve y ordenado.

## Salida

```json
{"rules": [], "examples": [], "mode_instruction": "", "correction_policy": ""}
```

