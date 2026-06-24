#!/usr/bin/env python3
"""Smoke tests for Samson Vision Runtime."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


def run(args: list[str], expect_ok: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [PYTHON, *args],
        cwd=ROOT.parents[1],
        text=True,
        capture_output=True,
    )
    if expect_ok and result.returncode != 0:
        raise AssertionError(f"Command failed: {args}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    if not expect_ok and result.returncode == 0:
        raise AssertionError(f"Command unexpectedly passed: {args}\nSTDOUT:\n{result.stdout}")
    return result


def parse_jsonl() -> None:
    index = ROOT / "rag_index.jsonl"
    for line_number, line in enumerate(index.read_text(encoding="utf-8-sig").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        item = json.loads(line)
        path = ROOT / item["path"]
        if not path.exists():
            raise AssertionError(f"Missing indexed path at line {line_number}: {path}")


def main() -> int:
    parse_jsonl()

    for pack in sorted((ROOT / "examples" / "good").glob("*.md")):
        run(["outputs/samson_vision_runtime/scripts/validate_pack.py", str(pack)])

    for pack in sorted((ROOT / "examples" / "bad").glob("*.md")):
        run(["outputs/samson_vision_runtime/scripts/validate_pack.py", str(pack)], expect_ok=False)

    prompt_out = ROOT / "prompt_web_agent_action.generated.md"
    run([
        "outputs/samson_vision_runtime/scripts/samson_vision_runtime.py",
        "build-prompt",
        "--domain",
        "web",
        "--mode",
        "agent_action",
        "--tool-context",
        str(ROOT / "examples" / "tool_context" / "web_google_tool_context.json"),
        "--out",
        str(prompt_out),
    ])
    prompt_text = prompt_out.read_text(encoding="utf-8")
    required_fragments = [
        "SAMSON_VISION_PACK v1",
        "04_LAYOUT_PATTERNS.md",
        "05_WEB_PATTERNS.md",
        "TOOL CONTEXT",
        "bad_excel_inferred_formula.md",
    ]
    for fragment in required_fragments:
        if fragment not in prompt_text:
            raise AssertionError(f"Prompt missing fragment: {fragment}")

    run([
        "outputs/samson_vision_runtime/scripts/samson_vision_runtime.py",
        "search-rag",
        "modal button",
        "--domain",
        "gui",
    ])

    deepseek_out = ROOT / "deepseek_prompt.generated.md"
    run([
        "outputs/samson_vision_runtime/scripts/demo_text_only_model.py",
        str(ROOT / "examples" / "good" / "web_google_home_pack.md"),
        "--out",
        str(deepseek_out),
    ])
    if "TEXT-ONLY MODEL PROMPT" not in deepseek_out.read_text(encoding="utf-8"):
        raise AssertionError("DeepSeek prompt not generated correctly.")

    print("SMOKE_TEST: true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
