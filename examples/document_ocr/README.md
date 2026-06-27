# Document OCR example

**Input:** `genesis_tablet_golden.png` — text-in-image tablet (682×1024).

**Output:** `output.svp.md` — OCR_TEXT + layout for document ingestion.

Best with Tesseract (`spa+eng`). Without it, contrast-based text zones are still emitted in UNCERTAINTIES.
