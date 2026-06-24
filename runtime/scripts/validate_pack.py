#!/usr/bin/env python3
"""Rule-based validator for SAMSON_VISION_PACK v1 Markdown outputs."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


REQUIRED_FIELDS = [
    "IMAGE_TYPE",
    "GLOBAL_SUMMARY",
    "VISUAL_HIERARCHY",
    "LAYOUT_MAP",
    "OCR_TEXT",
    "OBJECTS_AND_COMPONENTS",
    "COLOR_MAP",
    "DENSITY_MAP",
    "ASCII_REPRESENTATION",
    "USER_ACTIONS",
    "UNCERTAINTIES",
    "DO_NOT_ASSUME",
    "FINAL_INTERPRETATION_FOR_TEXT_ONLY_AI",
]

COORD_RE = re.compile(r"\[(\d+(?:\.\d+)?),\s*(\d+(?:\.\d+)?),\s*(\d+(?:\.\d+)?),\s*(\d+(?:\.\d+)?)\]")


def field_body(text: str, field: str) -> str:
    pattern = rf"(?ms)^{re.escape(field)}:\s*(.*?)(?=^[A-Z_]+:|\Z)"
    match = re.search(pattern, text)
    return match.group(1).strip() if match else ""


def validate(text: str) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if "[SAMSON_VISION_PACK v1]" not in text:
        errors.append("Missing header [SAMSON_VISION_PACK v1].")

    for field in REQUIRED_FIELDS:
        body = field_body(text, field)
        if not body:
            errors.append(f"Missing or empty field: {field}.")

    coords = COORD_RE.findall(text)
    if not coords:
        errors.append("No normalized coordinate boxes found.")
    else:
        for box in coords:
            values = [float(value) for value in box]
            if any(value < 0 or value > 100 for value in values):
                errors.append(f"Coordinate out of range 0-100: {box}.")
            if values[0] > values[2] or values[1] > values[3]:
                errors.append(f"Coordinate box has inverted corners: {box}.")

    uncertainty = field_body(text, "UNCERTAINTIES").lower()
    if "none" in uncertainty and len(uncertainty) < 20:
        warnings.append("UNCERTAINTIES says none; verify this is realistic.")
    if not any(token in text.lower() for token in ["confidence", "confianza"]):
        warnings.append("No confidence markers found.")

    do_not_assume = field_body(text, "DO_NOT_ASSUME")
    if len(do_not_assume.split()) < 5:
        warnings.append("DO_NOT_ASSUME is very short.")

    user_actions = field_body(text, "USER_ACTIONS")
    if user_actions and "[" not in user_actions:
        warnings.append("USER_ACTIONS has no coordinates; agent action may be weak.")

    return not errors, errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate SAMSON_VISION_PACK v1")
    parser.add_argument("pack", type=Path)
    args = parser.parse_args()

    text = args.pack.read_text(encoding="utf-8")
    ok, errors, warnings = validate(text)

    print(f"VALID: {str(ok).lower()}")
    if errors:
        print("\nERRORS:")
        for error in errors:
            print(f"- {error}")
    if warnings:
        print("\nWARNINGS:")
        for warning in warnings:
            print(f"- {warning}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

