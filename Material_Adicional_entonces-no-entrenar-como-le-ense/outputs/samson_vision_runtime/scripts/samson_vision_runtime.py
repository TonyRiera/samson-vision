#!/usr/bin/env python3
"""Minimal Samson Vision Runtime.

Builds a retrieval bundle and a prompt for a vision model. It does not call any
model API; it prepares the contract that any vision model should follow.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE = ROOT / "knowledge"
HARNESS = ROOT / "harness" / "samson_vision_harness.md"
MASTER_PROMPT = ROOT / "prompts" / "vision_model_master_prompt.md"
GOOD_EXAMPLES = ROOT / "examples" / "good"
BAD_EXAMPLES = ROOT / "examples" / "bad"
RAG_INDEX = ROOT / "rag_index.jsonl"

ALWAYS_LOAD = [
    "00_CORE_RULES.md",
    "01_OUTPUT_SCHEMA.md",
    "11_UNCERTAINTY_AND_ANTI_HALLUCINATION.md",
    "14_VALIDATION_CHECKLIST.md",
]

DOMAIN_FILES = {
    "generic": ["16_GENERIC_IMAGE_AND_CHART_PATTERNS.md"],
    "photo": ["16_GENERIC_IMAGE_AND_CHART_PATTERNS.md"],
    "chart": ["16_GENERIC_IMAGE_AND_CHART_PATTERNS.md"],
    "web": ["05_WEB_PATTERNS.md"],
    "excel": ["06_EXCEL_PATTERNS.md"],
    "spreadsheet": ["06_EXCEL_PATTERNS.md"],
    "dashboard": ["07_DASHBOARD_PATTERNS.md"],
    "document": ["08_DOCUMENT_PATTERNS.md"],
    "pdf": ["08_DOCUMENT_PATTERNS.md"],
    "gui": ["09_GUI_SOFTWARE_PATTERNS.md"],
    "software": ["09_GUI_SOFTWARE_PATTERNS.md"],
}

MODE_NOTES = {
    "fast": "Return summary, basic layout, OCR, uncertainties and next visual question.",
    "standard": "Return the full SAMSON_VISION_PACK v1.",
    "deep": "Return full pack, dense ASCII, uncertainty analysis and validation-aware details.",
    "agent_action": "Return full pack optimized for safe agent actions with coordinates.",
}

DOMAIN_EXAMPLES = {
    "generic": ["generic_photo_scene_pack.md"],
    "photo": ["generic_photo_scene_pack.md"],
    "chart": ["chart_bar_pack.md"],
    "web": ["web_google_home_pack.md"],
    "excel": ["excel_sales_table_pack.md"],
    "spreadsheet": ["excel_sales_table_pack.md"],
    "dashboard": ["dashboard_kpi_pack.md"],
    "document": ["document_invoice_pack.md"],
    "pdf": ["document_invoice_pack.md"],
    "gui": ["gui_error_dialog_pack.md"],
    "software": ["gui_error_dialog_pack.md"],
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def retrieve(domain: str) -> list[Path]:
    files = [KNOWLEDGE / name for name in ALWAYS_LOAD]
    files.extend(KNOWLEDGE / name for name in DOMAIN_FILES.get(domain, []))
    files.extend([
        KNOWLEDGE / "02_COLOR_LEXICON.md",
        KNOWLEDGE / "03_SHAPES_AND_SYMBOLS.md",
        KNOWLEDGE / "04_LAYOUT_PATTERNS.md",
        KNOWLEDGE / "10_ASCII_BRAILLE_UNICODE_METHODS.md",
        KNOWLEDGE / "15_DOMAIN_PROMPTS.md",
    ])
    return files


def example_paths(domain: str, include_bad: bool) -> list[Path]:
    paths = [GOOD_EXAMPLES / name for name in DOMAIN_EXAMPLES.get(domain, [])]
    if include_bad:
        paths.extend(sorted(BAD_EXAMPLES.glob("*.md"))[:2])
    return paths


def search_index(query: str, domain: str | None = None) -> list[dict[str, str]]:
    terms = {term.lower() for term in query.split() if term.strip()}
    matches: list[tuple[int, dict[str, str]]] = []
    for line in RAG_INDEX.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line:
            continue
        item = json.loads(line)
        if domain and item["domain"] not in {domain, "all"}:
            continue
        haystack = " ".join(str(value) for value in item.values()).lower()
        score = sum(1 for term in terms if term in haystack)
        if score:
            matches.append((score, item))
    matches.sort(key=lambda pair: pair[0], reverse=True)
    return [item for _, item in matches]


def build_prompt(domain: str, mode: str, include_bad: bool, tool_context: Path | None = None) -> str:
    parts = [
        "# VISION BRIDGE RUNTIME PROMPT",
        f"DOMAIN: {domain}",
        f"MODE: {mode}",
        f"MODE_INSTRUCTION: {MODE_NOTES[mode]}",
        "",
        "## MASTER PROMPT",
        read(MASTER_PROMPT),
        "",
        "## HARNESS",
        read(HARNESS),
        "",
        "## RETRIEVED RAG CONTEXT",
    ]
    for path in retrieve(domain):
        parts.append(f"\n### {path.name}\n")
        parts.append(read(path))
    examples = example_paths(domain, include_bad)
    if examples:
        parts.append("\n## FEW-SHOT EXAMPLES\n")
        for path in examples:
            parts.append(f"\n### {path.relative_to(ROOT)}\n")
            parts.append(read(path))
    if tool_context:
        parts.append("\n## TOOL CONTEXT\n")
        parts.append(read(tool_context))
    parts.append(
        "\n## TASK\n"
        "Analyze the provided image/capture. Generate only SAMSON_VISION_PACK v1. "
        "If OCR/DOM/tool observations are provided, cite them inside the proper fields. "
        "Do not invent missing text or off-screen elements."
    )
    return "\n".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(description="Samson Vision Runtime")
    sub = parser.add_subparsers(dest="command", required=True)

    prompt = sub.add_parser("build-prompt", help="Build prompt bundle for a vision model")
    prompt.add_argument("--domain", default="web", choices=sorted(DOMAIN_FILES.keys()))
    prompt.add_argument("--mode", default="agent_action", choices=sorted(MODE_NOTES.keys()))
    prompt.add_argument("--no-bad-examples", action="store_true")
    prompt.add_argument("--tool-context", type=Path)
    prompt.add_argument("--out", type=Path)

    search = sub.add_parser("search-rag", help="Search local RAG metadata")
    search.add_argument("query")
    search.add_argument("--domain", choices=sorted(DOMAIN_FILES.keys()))
    search.add_argument("--limit", type=int, default=8)

    args = parser.parse_args()

    if args.command == "build-prompt":
        output = build_prompt(
            args.domain,
            args.mode,
            include_bad=not args.no_bad_examples,
            tool_context=args.tool_context,
        )
        if args.out:
            args.out.write_text(output, encoding="utf-8")
        else:
            print(output)
    elif args.command == "search-rag":
        for item in search_index(args.query, args.domain)[: args.limit]:
            print(json.dumps(item, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
