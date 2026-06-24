# 🦁 Samson Vision — Public Documentation

> [README.md](../README.md) | [ARCHITECTURE.md](docs/ARCHITECTURE.md) | [SAMSON_VISION_PACK.md](docs/SAMSON_VISION_PACK.md) | [BENCHMARK.md](docs/BENCHMARK.md) | [SETUP.md](docs/SETUP.md) | [COSTS.md](docs/COSTS.md)

## What's here

This directory contains the public-facing documentation for Samson Vision.
All sensitive or personal information has been removed.

- **README.md** — Project overview, quick start, feature highlights
- **ARCHITECTURE.md** — Technical architecture and data flow
- **SAMSON_VISION_PACK.md** — Complete SVP format specification
- **BENCHMARK.md** — Model comparison with 24+ models
- **SETUP.md** — Installation guide for all platforms
- **COSTS.md** — Usage costs by provider and model

## Publishing

To publish this to GitHub:

```bash
# Option 1: Copy to a separate repo
cp -r PUBLIC /path/to/your-repo/
cd /path/to/your-repo
git init
git add .
git commit -m "Initial commit: Samson Vision docs"
git remote add origin https://github.com/your-username/samson-vision.git
git push -u origin main

# Option 2: Include in the main repo (exclude src/ and test/ if private)
git add PUBLIC/
git commit -m "Add public documentation"
```

## Sanitization checklist

Before publishing, ensure:

- [ ] No API keys, tokens, or secrets
- [ ] No personal paths (~/ or /home/username)
- [ ] No internal server addresses
- [ ] No subscription plan details tied to specific accounts
- [ ] No personal names or identifiers
- [ ] No internal tool configurations
- [ ] Costs are general estimates, not personal bills

## License

MIT
