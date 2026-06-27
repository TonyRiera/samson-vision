# Integrations — optional author tooling

> Updated: 27-Jun-2026

These integrations are **optional**. Samson Vision works standalone from GitHub via `pip install` and the CLI. This page documents how the author connects SVP output to Hermes, MiniMax, OpenCode, and Codex — not required for external users.

---

## Hermes Agent skill

Samson Vision is available as a Hermes skill in the author's environment:

```bash
hermes -s samson-vision chat -q "Analiza esta imagen: /ruta/imagen.jpg"
```

The skill provides three interpretation modes:

| Mode | Backend | Typical speed |
|------|---------|---------------|
| Fast | MiniMax-M2.1 (mmx CLI) | ~5s |
| Balanced | minimax-m2.5 (OpenCode) | ~11s |
| Precise | kimi-k2.7-code (OpenCode) | ~8s |

---

## Interpret SVP with a text LLM

SVP is plain text — pass it to any language model:

### MiniMax M2.1 (mmx CLI)

```bash
SVP=$(samson-vision imagen.png --md 2>/dev/null)
echo "$SVP" | mmx text chat --model MiniMax-M2.1 \
  --system "Interpreta este SAMSON_VISION_PACK como si vieras la imagen." \
  --message "$SVP" --temp 0.3
```

### OpenCode Go (minimax-m2.5)

```bash
SVP=$(samson-vision imagen.png --md 2>/dev/null)
curl -s https://opencode.ai/zen/go/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENCCODE_API_KEY" \
  -d "{\"model\":\"minimax-m2.5\", \"messages\":[{\"role\":\"system\",\"content\":\"Interpreta este SAMSON_VISION_PACK.\"},{\"role\":\"user\",\"content\":\"$SVP\"}]}"
```

### Codex CLI (ChatGPT Plus)

```bash
SVP=$(samson-vision imagen.png --md 2>/dev/null)
codex -z "Eres Samson Vision. Interpreta este SAMSON_VISION_PACK: $SVP"
```

---

## Fallback harness order

Recommended order for interpreting SVP with external models:

```
PASO 1: MiniMax-M2.1 (mmx CLI)       → 5s   → $0.0008/query → 6/6 binary signals
PASO 2: minimax-m2.5 (OpenCode Go)    → 11s  → $0.0009/query → 5/6 binary signals
PASO 3: kimi-k2.7-code (OpenCode Go)  → 8s   → $0.003/query  → 6/6 binary signals
PASO 4: gpt-5.4-mini (Codex CLI)      → 8s   → ~$0.0005/q     → 6/6 binary signals
```

**Models that do not interpret SVP well:** deepseek flash v4, GLM-5.x, qwen3.7-max, kimi-k2.6/k2.5

See [BENCHMARK.md](BENCHMARK.md) for full results.

---

## `harnesses.py` in the package

The `harnesses.py` module ships with the package for author-side connectors (`SAMSON_VISION_HOME`, model routing). External users can ignore it unless building custom agent workflows.
