# Nous Agent Blueprint

## Objetivo

Dar visión indirecta a modelos sin visión mediante subagentes especializados.

## Grafo de subagentes

```text
orchestrator
  ├─ rag_retriever
  ├─ vision_scout
  ├─ ocr_agent
  ├─ layout_agent
  ├─ pack_writer
  ├─ validator_agent
  └─ text_reasoner
```

## Contratos

### `rag_retriever`

Entrada:

```json
{"domain": "web", "mode": "agent_action"}
```

Salida:

```json
{"harness": "...", "rules": ["..."], "examples": ["..."]}
```

### `vision_scout`

Entrada:

```json
{"image": "<image>", "prompt_bundle": "..."}
```

Salida:

```json
{"draft_pack": "[SAMSON_VISION_PACK v1]..."}
```

### `validator_agent`

Entrada:

```json
{"draft_pack": "..."}
```

Salida:

```json
{"valid": true, "errors": [], "warnings": []}
```

### `text_reasoner`

Entrada:

```json
{"pack": "...", "task": "what should the agent do next?"}
```

Salida:

```json
{"understanding": "...", "next_actions": ["..."], "needs_more_visual_info": false}
```

## Política

Si el validador falla, el orquestador no debe enviar el pack a DeepSeek todavía. Debe pedir corrección al modelo con visión usando `prompts/correction_prompt.md`.

