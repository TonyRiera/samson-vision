# Examples — Samson Vision v0.3

Five real SVP outputs generated from curated assets in [`assets/`](../assets/). Each folder contains `input.png`, `output.svp.md`, and a short README.

| Folder | Asset source | Use case |
|--------|--------------|----------|
| [`web_ui_screenshot/`](web_ui_screenshot/) | `tablets_and_code.png` | Code/UI composition — layout + text zones |
| [`dashboard/`](dashboard/) | `pillars_as_data.png` | Data-heavy visual — KPI-style density |
| [`terminal_error/`](terminal_error/) | `blueprint_weak_points.png` | Structural diagram / error annotation |
| [`document_ocr/`](document_ocr/) | `genesis_tablet_golden.png` | Text-in-image / document OCR |
| [`mobile_ui/`](mobile_ui/) | `samson_anointed_chains.png` | Portrait aspect — mobile-like framing |

## Regenerate

```bash
pip install -e ".[dev]"
samson-vision examples/document_ocr/input.png --md > examples/document_ocr/output.svp.md
```

Or via Python API:

```bash
python3 -c "from samson_vision import generate_svp; print(generate_svp('examples/web_ui_screenshot/input.png'))"
```

> **Note:** With Tesseract installed (Linux/macOS/claw), `OCR_TEXT` includes real strings. Without it, the pipeline falls back to contrast-based text zones — SVP structure is still valid.
