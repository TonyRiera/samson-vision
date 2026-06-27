# Benchmark plan — v0.4 (stub)

> **Status:** planned, not executed in v0.3.0. This document defines scope only.

## Goal

Run Samson Vision + LLM interpretation on **20 curated images** across 5 categories and report **binary signal recovery** (not subjective "100% quality").

## Image set (planned)

| # | Category | Source | Signals to check |
|---|----------|--------|------------------|
| 1–4 | Web UI | Real screenshots (El Mundo, forms, nav) | headline, date, nav, CTA |
| 5–8 | Dashboard | KPI cards, charts-as-screenshots | title, metric values, legend |
| 9–12 | Terminal / errors | CLI logs, stack traces | error type, file:line, command |
| 13–16 | Documents | Invoices, tablets, scanned PDFs | OCR fields, table rows |
| 17–20 | Mobile UI | Portrait layouts, touch targets | header, primary action, scroll hint |

## Metrics

- **Primary:** N/M binary signals recovered per image (same methodology as El Mundo 6/6 test)
- **Secondary:** SVP generation time, OCR word recall vs ground truth
- **Not claimed:** ML object detection accuracy, medical/legal suitability, pixel-perfect logo fidelity

## Deliverables (v0.4)

- [ ] `bench/` package with reproducible runner
- [ ] `bench/fixtures/` — 20 PNGs + ground-truth JSON
- [ ] `bench/results/` — per-model CSV + summary markdown
- [ ] CI job: generate SVP only (no LLM keys in public CI)

## Monorepo split (same milestone)

```
samson-vision/
├── core/     ← SVP pipeline (samson_core, vmk, samson_vision)
├── agent/    ← harnesses, runtime integration
└── bench/    ← this benchmark suite
```

See README roadmap section for v0.4 timeline.
