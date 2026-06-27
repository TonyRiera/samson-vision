<p align="center">
  <img src="../assets/final_moment_pillars.png" width="560" alt="Samson Vision">
</p>

<h1 align="center">Samson Vision</h1>

<p align="center">
  Turns images into structured text so text-only models can reason over screenshots, documents, and screens.<br>
  Does not fully replace a vision model. A cheap, auditable, versionable bridge.
</p>

<p align="center">
  <em>Your limitations are not an impossible limit to overcome.</em> <em>Philippians 4:13</em>
</p>

<p align="center">
  <a href="docs/SETUP.md"><strong>Install</strong></a>
  &nbsp;·&nbsp;
  <a href="../index.html"><strong>Landing</strong></a>
  &nbsp;·&nbsp;
  <a href="docs/SAMSON_VISION_PACK.md"><strong>SVP Spec</strong></a>
</p>

## When to use

| ✅ Use SVP | ❌ Do not rely on SVP alone |
|------------|----------------------------|
| Screenshots, dashboards, forms | Fine photo detail |
| OCR + layout, scanned documents | Facial recognition |
| Cheap text-only agents | Critical medical/legal decisions |
| CI/QA with versionable capture diffs | Pixel-perfect logos/icons |
| Orchestrators delegating to vision subagents | When fidelity > cost |

> Samson Vision is a visual-text bridge: it does not give an AI real eyes, but delivers structured, auditable, cheap description so an LLM can reason over the textual translation — not "see" like a native multimodal model.

---

## Metaphor

Samson could see even without eyes — his vision was God's plan, not his retina. Samson Vision offers **operational sight for eyeless AI**: the agent stays the same text model, but receives visual context through SVP before acting or delegating.

---

## How it really works (technical)

Samson Vision **does not turn a text AI into a vision model**. It delivers a **structured translation** — the **SAMSON_VISION_PACK (SVP)** — with 13 layers: OCR, coordinates, ASCII (8 styles), colors, density, hierarchy, visual region detection (OpenCV, not ML object detection), and anti-hallucination guardrails.

Generation pipeline is **0% AI**: numpy + OpenCV + Tesseract. A **compatible LLM can reason over the textual translation** — not all models interpret SVP well (see benchmark).

---

## Usage modes A / B / C

| Mode | Description | When |
|------|-------------|------|
| **A — SVP + text LLM** | SVP pipeline + text-only model | Cheap agent, OCR/layout, CI diff |
| **B — SVP orients + subagent validates** | Visionless orchestrator reads SVP → delegates to vision subagent (Jordan/Hermes flow) | UI review, accessibility, regressions |
| **C — Direct vision** | Native multimodal on the image | Fidelity > cost: photos, logos, fine detail |

---

## Subagent workflow (Mode B)

| Role | Typical model | Native vision | Function |
|------|---------------|:-------------:|----------|
| **Main agent** | DeepSeek Flash v4 | ❌ No | Coordinates, reads SVP, delegates |
| **Vision subagent** | vision_scout / multimodal | ✅ Yes | Analyzes image, validates pack |
| **Samson Vision CLI** | Algorithmic pipeline | — | Generates SVP (0% AI) |

The main agent runs `samson-vision image.png --md` **before delegating**. The vision subagent receives image + embedded SVP.

> **Benchmark note:** DeepSeek Flash v4 reads SVP as orchestrator but returns empty as SVP interpreter via API — use MiniMax/kimi for LLM pack interpretation.

---

## Honest limitations

### Works well
- UI screenshots, dashboards, web forms
- Documents with readable text (OCR + layout)
- CI/QA with versionable SVP diffs

### Works adequately
- Low-contrast images or small fonts
- Complex diagrams without embedded text

### Do not rely on SVP alone
- Artistic photography or fine texture detail
- Facial recognition or visual identity
- Critical medical, legal, or safety decisions
- Pixel-perfect logos → **Mode C**

---

## Quick start

```bash
samson-vision image.png --md > pack.md

python3 -c "from samson_vision import generate_svp; print(generate_svp('image.png', fmt='md'))"
```

## Key features

- **8 ASCII styles**, real OCR (Tesseract), visual region detection via OpenCV
- **29 basic unit tests** — not "complete visual comprehension"
- **Zero vision API calls** in the generation pipeline

## Benchmark summary

Metric: **6/6 signals** on El Mundo test screenshot — not "100% visual quality". See [BENCHMARK.md](docs/BENCHMARK.md).

| Tier | Models | Signals | Speed |
|------|--------|:-------:|:-----:|
| 🥇 Best | MiniMax-M2.1, kimi-k2.7-code | 6/6 | 5-8s |
| 🥈 Great value | minimax-m2.5 | 5/6 | 11s |
| 🥉 Solid | GPT-5.4-mini, MiniMax-M3 | 4-6/6 | 8-27s |
| ❌ Incompatible | deepseek flash v4, glm-5.x | 0/6 | — |

## Architecture

```
samson-vision/
├── src/samson_vision.py    ← SVP generator + generate_svp() API
├── test/run_tests.py       ← 29 basic unit tests
└── examples/             ← planned examples (stub)
```

## License

MIT
