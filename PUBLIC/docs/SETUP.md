# Setup Guide

## Requirements

- Python 3.10+
- Tesseract OCR (for text extraction)
- OpenCV (optional, for improved object detection)
- A text-only LLM API (OpenAI, Anthropic, MiniMax, etc.)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/samson-vision.git
cd samson-vision
```

### 2. Install Python dependencies

It's recommended to use a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or: .venv\Scripts\activate  # Windows
```

```bash
pip install pillow numpy
```

Optional dependencies for improved detection:

```bash
pip install opencv-python-headless  # Better edge detection
pip install pytesseract             # OCR (requires tesseract binary)
```

### 3. Install Tesseract OCR

**Linux (apt):**
```bash
sudo apt install tesseract-ocr tesseract-ocr-spa tesseract-ocr-eng
```

**macOS (brew):**
```bash
brew install tesseract
```

**Windows:**
Download from [GitHub tesseract-ocr/tesseract](https://github.com/tesseract-ocr/tesseract)

### 4. Verify installation

```bash
python3 test/run_tests.py
# Expected output: 29/29 tests passed
```

## Quick test

```bash
# Generate an SVP from any image
python3 src/samson_vision.py path/to/image.png --md

# Or with a specific domain hint
python3 src/samson_vision.py path/to/screenshot.png --md --prompt "Describe this web page"
```

## Using with LLM providers

The SVP is pure text — you can feed it to any LLM API. Here are examples:

### OpenAI (GPT-4o-mini, etc.)

```python
import openai

vbp = open("pack.md").read()
response = openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are Samson Vision. Interpret this SAMSON_VISION_PACK as if you were seeing the image. Describe what you see."},
        {"role": "user", "content": vbp}
    ]
)
print(response.choices[0].message.content)
```

### MiniMax API

```bash
mmx text chat --model MiniMax-M2.1 \
  --system "Eres Samson Vision. Interpreta este SAMSON_VISION_PACK." \
  --message "$(cat pack.md)" \
  --temp 0.3
```

### OpenCode Go API

```bash
curl -s https://opencode.ai/zen/go/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $YOUR_KEY" \
  -d '{
    "model": "minimax-m2.5",
    "messages": [
      {"role": "system", "content": "You are Samson Vision. Interpret this SVP."},
      {"role": "user", "content": "'$(cat pack.md)'"}
    ]
  }'
```

### Any OpenAI-compatible endpoint

```python
# Works with any provider that supports /v1/chat/completions
# Just change base_url and api_key
```

## Using with Hermes Agent

Samson Vision integrates with [Hermes Agent](https://hermes-agent.nousresearch.com) as a skill:

```bash
hermes -s samson-vision chat -q "Describe this image"
```

The skill provides three modes: fast (MiniMax-M2.1), balanced (minimax-m2.5), and precise (kimi-k2.7-code). See [`src/harnesses.py`](../../src/harnesses.py) for the integration layer.

## OCR troubleshooting

If Tesseract returns `[text_zone]` placeholders instead of real text:

1. **Check tesseract is installed**: `tesseract --version`
2. **Set the binary path explicitly**:
```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
```
3. **The code auto-detects** common paths (brew, apt, /usr/local), but you can override:
```python
os.environ["TESSDATA_PREFIX"] = "/path/to/tessdata"
```

For web screenshots with small text, the built-in preprocessing (2x upscale + OTSU binarization) handles most cases. If text is still missed, increase the resolution of the input image before processing.
