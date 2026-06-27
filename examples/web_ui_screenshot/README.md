# Web UI screenshot example

**Input:** `tablets_and_code.png` — tablets + code overlay (1024×1536).

**Output:** `output.svp.md` — SVP with layout map, visual hierarchy, and OCR zones.

```bash
samson-vision input.png --md > output.svp.md
```

Typical use: agent receives a browser screenshot; orchestrator reads SVP before delegating to a vision subagent.
