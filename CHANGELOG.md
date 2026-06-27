# Changelog

## [0.3.2] — 2026-06-27

**Packaging fix** — explicit `package-dir` for setuptools src layout.

### Changed
- Added `[tool.setuptools] package-dir = {"" = "src"}` for reliable editable/install imports
- SETUP.md harness table: 6/6 binary signals (not "% calidad" claims)
- README roadmap: v0.3.1 release notes + packaging cleanup

### Verified
- Test suite 29/29


All notable changes to Samson Vision are documented here.

## [0.3.1] — 2026-06-27

**Packaging & clarity patch** after v0.3.0 validation.

### Changed
- `PACKAGE_VERSION` / pyproject aligned to `0.3.1`
- SVP pack `version` field aligned to schema `1.0` (`SVP_SCHEMA_VERSION`)
- README: CI badge, early-release disclaimer
- Project description focused on visual-to-text agent workflows

### Verified
- Clean `pip install git+https://github.com/TonyRiera/samson-vision.git` import path
- Test suite 29/29

## [0.3.0] — 2026-06-27

**Credibility release** — public positioning, CI, and real examples without claiming full vision parity.

### Added
- README ideal: EN lead + ES, comparison table, niche positioning, separate metaphor vs technical sections
- `generate_svp()` public API documented and verified
- `SAMSON_VISION_HOME` env override in `harnesses.py`
- GitHub Actions CI (Python 3.10 / 3.11 / 3.12, `pip install -e .`, `test/run_tests.py`)
- `examples/` with 5 categories: `web_ui_screenshot`, `dashboard`, `terminal_error`, `document_ocr`, `mobile_ui`
- Real `output.svp.md` files generated from `assets/` via CLI
- `BENCHMARK_v0.4.md` — stub plan for 20-image benchmark (not executed in this release)
- Roadmap v0.4 in README (monorepo split core/agent/bench deferred)

### Fixed / clarified
- Benchmark claims: **6/6 binary signals**, not "100% visual quality"
- `OBJECTS_AND_COMPONENTS`: **visual region detection** (OpenCV), not ML object detection
- Version aligned to semver `0.3.0` (was `2.0` internally)

### Unchanged (roadmap v0.4)
- Full monorepo split (`core/`, `agent/`, `bench/`)
- 20-image benchmark suite execution
- Production Hermes/Jordan harness hardening on claw

## [0.2.x] — prior internal releases

- SVP 13-field schema, VMK pipeline, 29 unit tests, MiniMax/kimi benchmark on El Mundo screenshot
