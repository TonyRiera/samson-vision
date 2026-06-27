# SETUP — Samson Vision installation

> Updated: 27-Jun-2026 | Verified: 29/29 tests + SVP functional

Public setup guide for external users installing from GitHub only. For optional author integrations (Hermes, MiniMax, Codex), see [INTEGRATIONS.md](INTEGRATIONS.md).

---

## Requirements

- **OS:** Linux, macOS, or Windows
- **Python:** 3.10+
- **Git:** only if cloning (Option B)

| Profile | Python packages | System binary |
|---------|-----------------|---------------|
| **Minimum** | `pillow`, `numpy` | — |
| **Recommended** | `[dev]` extras: `opencv-python-headless`, `pytesseract` | **Tesseract 5+** |

---

## Install

### Option A — pip one-liner (no clone)

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install "samson-vision[dev] @ git+https://github.com/TonyRiera/samson-vision.git@v0.3.3"
```

### Option B — clone + setup script

```bash
git clone https://github.com/TonyRiera/samson-vision.git
cd samson-vision
bash setup.sh --dev
```

`setup.sh` creates a venv, installs dependencies, installs the package editable, and runs the test suite.

### Option C — clone + manual venv

```bash
git clone https://github.com/TonyRiera/samson-vision.git
cd samson-vision
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
mkdir -p input output
```

---

## Tesseract (recommended)

Tesseract improves the `OCR_TEXT` field. Without it, the pipeline still runs but OCR zones stay generic.

**Ubuntu / Debian:**

```bash
sudo apt install tesseract-ocr tesseract-ocr-spa tesseract-ocr-eng
```

**macOS:**

```bash
brew install tesseract
```

**Windows:** download the installer from [tesseract-ocr/tesseract](https://github.com/tesseract-ocr/tesseract).

> **No sudo:** build from source with `--prefix=$HOME/local`, use `conda install -c conda-forge tesseract`, or skip Tesseract — the pipeline works without OCR text extraction.

---

## Verify install

```bash
# CLI entry point
samson-vision --help

# Python API
python3 -c "from samson_vision import generate_svp; print('samson-vision', generate_svp.__name__)"

# Run tests (requires clone or git checkout)
python3 test/run_tests.py
```

Expected: **29/29** tests passing.

---

## Quick test — generate an SVP

### If you cloned the repo

```bash
source .venv/bin/activate
samson-vision assets/samson_pillars_crumbling.png --md
```

### Pip-only (no clone) — download a sample image

```bash
curl -sL -o /tmp/sv-test.png \
  "https://raw.githubusercontent.com/TonyRiera/samson-vision/v0.3.3/assets/samson_pillars_crumbling.png"
samson-vision /tmp/sv-test.png --md | head -30
```

### Python API

```bash
python3 -c "
from samson_vision import generate_svp
print(generate_svp('/tmp/sv-test.png', fmt='md')[:500])
"
```

Each run prints a decorative verse on **stderr** (does not affect stdout SVP). Use `2>/dev/null` to silence it.

Save output to a file:

```bash
samson-vision /tmp/sv-test.png --json > sample.svp.json
samson-vision /tmp/sv-test.png --md > sample.svp.md
```

---

## Project layout

```
samson-vision/
├── src/
│   ├── samson_vision.py         → SVP generator + generate_svp() API
│   ├── samson_core.py           → 8 ASCII styles
│   └── vmk/                     → Vision Multimodal Kernel
├── test/run_tests.py            → 29 tests
├── assets/                      → sample images (clone only)
├── setup.sh                     → automated install
├── pyproject.toml               → package metadata
└── PUBLIC/docs/                 → public documentation
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: PIL` | `pip install pillow` |
| `ModuleNotFoundError: numpy` | `pip install numpy` |
| `ModuleNotFoundError: cv2` | `pip install opencv-python-headless` or `pip install -e ".[dev]"` |
| `samson-vision: command not found` | Activate venv: `source .venv/bin/activate` |
| OCR shows `[text_zone]` | Install Tesseract (see above) |
| Empty SVP fields | Image has little processable content — try a richer screenshot |

---

## Notes

- Verses print to **stderr** only — never contaminate stdout
- Without Tesseract: OCR skips gracefully; pipeline stays functional
- Without OpenCV: region detection uses basic PIL (less precise)
- **No HTTP server** — CLI and Python API only
