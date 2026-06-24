"""
Samson Vision — Integration with Samson Vision Runtime.

Connects the visual analysis pipeline with the full runtime system:
- RAG knowledge retrieval (16 knowledge files by domain)
- SAMSON_VISION_PACK v1 validation
- Domain-specific patterns and rules
- Anti-hallucination enforcement
"""
import json
import re
from pathlib import Path
from typing import Optional

RUNTIME_DIR = Path.home() / "proyectos" / "samson-vision" / "runtime"
KNOWLEDGE_DIR = RUNTIME_DIR / "knowledge"
RAG_INDEX = RUNTIME_DIR / "rag_index.jsonl"
GOOD_EXAMPLES_DIR = RUNTIME_DIR / "examples" / "good"

REQUIRED_FIELDS = [
    "IMAGE_TYPE", "GLOBAL_SUMMARY", "VISUAL_HIERARCHY", "LAYOUT_MAP",
    "OCR_TEXT", "OBJECTS_AND_COMPONENTS", "COLOR_MAP", "DENSITY_MAP",
    "ASCII_REPRESENTATION", "USER_ACTIONS", "UNCERTAINTIES",
    "DO_NOT_ASSUME", "FINAL_INTERPRETATION_FOR_TEXT_ONLY_AI",
]

COORD_RE = re.compile(r"\[(\d+(?:\.\d+)?),\s*(\d+(?:\.\d+)?),\s*(\d+(?:\.\d+)?),\s*(\d+(?:\.\d+)?)\]")

# ─── RAG Retrieval ────────────────────────────────────────────

ALWAYS_LOAD = [
    "00_CORE_RULES.md", "01_OUTPUT_SCHEMA.md",
    "11_UNCERTAINTY_AND_ANTI_HALLUCINATION.md", "14_VALIDATION_CHECKLIST.md",
]

DOMAIN_FILES = {
    "generic": ["16_GENERIC_IMAGE_AND_CHART_PATTERNS.md"],
    "web": ["05_WEB_PATTERNS.md"],
    "excel": ["06_EXCEL_PATTERNS.md"],
    "dashboard": ["07_DASHBOARD_PATTERNS.md"],
    "document": ["08_DOCUMENT_PATTERNS.md"],
    "gui": ["09_GUI_SOFTWARE_PATTERNS.md"],
}


def retrieve_knowledge(domain: str = "web") -> list[dict]:
    """Retrieve knowledge files for a domain."""
    files = [KNOWLEDGE_DIR / name for name in ALWAYS_LOAD]
    files.extend(KNOWLEDGE_DIR / name for name in DOMAIN_FILES.get(domain, []))
    files.extend([
        KNOWLEDGE_DIR / "02_COLOR_LEXICON.md",
        KNOWLEDGE_DIR / "03_SHAPES_AND_SYMBOLS.md",
        KNOWLEDGE_DIR / "04_LAYOUT_PATTERNS.md",
        KNOWLEDGE_DIR / "10_ASCII_BRAILLE_UNICODE_METHODS.md",
    ])
    result = []
    for path in files:
        if path.exists():
            result.append({"name": path.name, "content": path.read_text(encoding="utf-8")})
    return result


def search_rag(query: str, domain: Optional[str] = None, limit: int = 5) -> list[dict]:
    """Search the RAG index by keywords."""
    terms = {t.lower() for t in query.split() if t.strip()}
    matches = []
    for line in RAG_INDEX.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line:
            continue
        item = json.loads(line)
        if domain and item.get("domain") not in {domain, "all"}:
            continue
        haystack = " ".join(str(v) for v in item.values()).lower()
        score = sum(1 for t in terms if t in haystack)
        if score:
            matches.append((score, item))
    matches.sort(key=lambda p: p[0], reverse=True)
    return [item for _, item in matches[:limit]]


def get_example(domain: str = "web") -> Optional[str]:
    """Get a good example pack for the domain."""
    mapping = {
        "web": "web_google_home_pack.md",
        "excel": "excel_sales_table_pack.md",
        "dashboard": "dashboard_kpi_pack.md",
        "document": "document_invoice_pack.md",
        "gui": "gui_error_dialog_pack.md",
        "generic": "generic_photo_scene_pack.md",
    }
    name = mapping.get(domain, "web_google_home_pack.md")
    path = GOOD_EXAMPLES_DIR / name
    if path.exists():
        return path.read_text(encoding="utf-8")
    return None


# ─── Validation ───────────────────────────────────────────────

def field_body(text: str, field: str) -> str:
    """Extract the body of an SVP field."""
    pattern = rf"(?ms)^{re.escape(field)}:\s*(.*?)(?=^[A-Z_]+:|\Z)"
    m = re.search(pattern, text)
    return m.group(1).strip() if m else ""


def validate_pack(text: str) -> dict:
    """Validate a SAMSON_VISION_PACK v1 output.
    
    Returns: {"valid": bool, "errors": [...], "warnings": [...]}
    """
    errors = []
    warnings = []

    if "[SAMSON_VISION_PACK v1]" not in text:
        errors.append("Missing header [SAMSON_VISION_PACK v1]")

    for field in REQUIRED_FIELDS:
        body = field_body(text, field)
        if not body:
            errors.append(f"Missing or empty field: {field}")

    coords = COORD_RE.findall(text)
    if not coords:
        warnings.append("No normalized coordinate boxes found")
    else:
        for box in coords:
            vals = [float(v) for v in box]
            if any(v < 0 or v > 100 for v in vals):
                errors.append(f"Coordinate out of range 0-100: {box}")
            if vals[0] > vals[2] or vals[1] > vals[3]:
                errors.append(f"Coordinate box inverted: {box}")

    uncert = field_body(text, "UNCERTAINTIES").lower()
    if "none" in uncert and len(uncert) < 20:
        warnings.append("UNCERTAINTIES says 'none' — probably incomplete")

    do_not = field_body(text, "DO_NOT_ASSUME").lower()
    if not do_not or len(do_not) < 10:
        warnings.append("DO_NOT_ASSUME is empty or too short")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "n_coords": len(coords),
    }


# ─── Build Knowledge Context ──────────────────────────────────

def build_knowledge_context(domain: str = "web", query: str = "") -> str:
    """Build a knowledge context string for prompt injection."""
    parts = ["[KNOWLEDGE CONTEXT]", ""]
    
    # Retrieved RAG documents
    for doc in retrieve_knowledge(domain):
        parts.append(f"--- {doc['name']} ---")
        parts.append(doc['content'][:500])
        parts.append("")
    
    # RAG search results
    if query:
        results = search_rag(query, domain)
        if results:
            parts.append("--- RAG SEARCH RESULTS ---")
            for r in results:
                parts.append(f"  [{r.get('id','?')}] {r.get('tags','')}")
            parts.append("")
    
    # Example
    ex = get_example(domain)
    if ex:
        parts.append("--- DOMAIN EXAMPLE ---")
        parts.append(ex[:800])
        parts.append("")
    
    return "\n".join(parts)


# ─── CLI ──────────────────────────────────────────────────────

def cli():
    import sys
    if len(sys.argv) < 2:
        print("Samson Vision Runtime Integration")
        print("Uso: runtime_integration.py <command> [args]")
        print("\nComandos:")
        print("  knowledge <domain>       — Mostrar conocimiento para dominio")
        print("  search <query> [domain]  — Buscar en RAG")
        print("  validate <archivo>        — Validar un SVP")
        print("  example <domain>         — Mostrar ejemplo del dominio")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "knowledge":
        domain = sys.argv[2] if len(sys.argv) > 2 else "web"
        ctx = build_knowledge_context(domain)
        print(ctx[:3000])
    
    elif cmd == "search":
        query = sys.argv[2] if len(sys.argv) > 2 else ""
        domain = sys.argv[3] if len(sys.argv) > 3 else None
        results = search_rag(query, domain)
        for r in results:
            print(f"  [{r.get('id','?')}] domain={r.get('domain','?')} path={r.get('path','?')}")
        if not results:
            print("  Sin resultados")
    
    elif cmd == "validate":
        path = sys.argv[2] if len(sys.argv) > 2 else ""
        text = Path(path).read_text(encoding="utf-8")
        result = validate_pack(text)
        print(f"Valid: {result['valid']}")
        if result['errors']:
            print(f"Errors ({len(result['errors'])}):")
            for e in result['errors']:
                print(f"  - {e}")
        if result['warnings']:
            print(f"Warnings ({len(result['warnings'])}):")
            for w in result['warnings']:
                print(f"  - {w}")
        print(f"Coordinates: {result['n_coords']}")
    
    elif cmd == "example":
        domain = sys.argv[2] if len(sys.argv) > 2 else "web"
        ex = get_example(domain)
        if ex:
            print(ex[:2000])
        else:
            print(f"No example for domain: {domain}")


if __name__ == "__main__":
    cli()
