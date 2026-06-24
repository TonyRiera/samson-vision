#!/usr/bin/env python3
"""Build the final prompt for a text-only model from a Samson Vision Pack."""

from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEXT_HARNESS = ROOT / "harness" / "deepseek_text_only_harness.md"


def main() -> int:
    parser = argparse.ArgumentParser(description="Create text-only model prompt")
    parser.add_argument("pack", type=Path)
    parser.add_argument("--question", default="Razona sobre la escena y propone el siguiente paso seguro.")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    output = "\n\n".join([
        "# TEXT-ONLY MODEL PROMPT",
        TEXT_HARNESS.read_text(encoding="utf-8"),
        "## USER QUESTION",
        args.question,
        "## SAMSON_VISION_PACK",
        args.pack.read_text(encoding="utf-8"),
    ])

    if args.out:
        args.out.write_text(output, encoding="utf-8")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

