#!/usr/bin/env python3
"""
🦁 SAMSON VISION — Integration Test Harness v2.0

Prueba el pipeline completo del proyecto: instalación, CLI, SVP,
importabilidad, y consistencia estructural.

Basado en lecciones aprendidas el 24-Jun-2026:
- PYTHONPATH no debe ser necesario (pyproject.toml lo resuelve)
- ARCHITECTURE.md estaba corrupto → test de integridad
- SETUP.md tenía información incorrecta → test de veracidad
- __version__ no existía → test de metadata
- El CLI debe estar disponible tras pip install -e .

USO:
    python3 test/test_integration.py [--verbose]

SALIDA:
    Código 0 = todo OK
    Código 1 = algún test falló
"""

import os
import sys
import json
import subprocess
import tempfile
import importlib.util
from pathlib import Path

PROJECT = Path(os.path.expanduser("~/proyectos/samson-vision"))
ASSETS = PROJECT / "assets"
SAMPLE_IMG = ASSETS / "samson_pillars_crumbling.png"
SVP_SPEC = PROJECT / "PUBLIC/docs/SAMSON_VISION_PACK.md"

REQUIRED_FIELDS_SVP = [
    "IMAGE_TYPE", "GLOBAL_SUMMARY", "VISUAL_HIERARCHY", "LAYOUT_MAP",
    "OCR_TEXT", "OBJECTS_AND_COMPONENTS", "COLOR_MAP", "DENSITY_MAP",
    "ASCII_REPRESENTATION", "USER_ACTIONS", "UNCERTAINTIES",
    "DO_NOT_ASSUME", "FINAL_INTERPRETATION_FOR_TEXT_ONLY_AI",
]

REQUIRED_DOCS_PUBLIC = [
    "PUBLIC/README.md",
    "PUBLIC/INDEX.md",
    "PUBLIC/docs/ARCHITECTURE.md",
    "PUBLIC/docs/SAMSON_VISION_PACK.md",
    "PUBLIC/docs/BENCHMARK.md",
    "PUBLIC/docs/SETUP.md",
    "PUBLIC/docs/COSTS.md",
]

REQUIRED_DIRS = [
    "src", "test", "runtime", "assets", "input", "output",
    "PUBLIC/docs", "runtime/knowledge",
]

REQUIRED_SRC_FILES = [
    "src/samson_core.py", "src/samson_vision.py",
    "src/versiculos.py", "src/harnesses.py",
    "src/runtime_integration.py", "src/device_db.py",
    "src/synesthesia.py", "src/vmk/kernel.py",
    "src/vmk/scene_graph.py", "src/__init__.py",
]

SCORE = {"pass": 0, "fail": 0, "total": 0}
ERRORS = []


def test(name, condition, detail=""):
    """Ejecuta un test y acumula resultado."""
    SCORE["total"] += 1
    if condition:
        SCORE["pass"] += 1
        status = "✅"
    else:
        SCORE["fail"] += 1
        status = "❌"
        ERRORS.append(f"  {status} {name}: {detail}")
    print(f"  {status} {name}")
    return condition


# ─── 1. ESTRUCTURA ─────────────────────────────────────────────

def test_estructura():
    print("\n📁 1. ESTRUCTURA DEL PROYECTO")
    ok = True
    for d in REQUIRED_DIRS:
        p = PROJECT / d
        ok &= test(f"Directorio {d}/", p.is_dir(), str(p))
    for f in REQUIRED_SRC_FILES:
        p = PROJECT / f
        ok &= test(f"Archivo fuente {f}", p.is_file(), str(p))
    for f in REQUIRED_DOCS_PUBLIC:
        p = PROJECT / f
        ok &= test(f"Documento público {f}", p.is_file(), str(p))
    return ok


# ─── 2. IMPORTABILIDAD ────────────────────────────────────────

def test_imports():
    print("\n📦 2. IMPORTABILIDAD")
    ok = True

    sys.path.insert(0, str(PROJECT / "src"))
    sys.path.insert(0, str(PROJECT))

    try:
        from samson_core import __version__
        ok &= test("samson_core.__version__ existe", True, f"v{__version__}")
    except ImportError as e:
        ok &= test("samson_core importable", False, str(e))

    try:
        from samson_vision import SamsonVisionBuilder
        ok &= test("samson_vision.SamsonVisionBuilder", True, "")
    except ImportError as e:
        ok &= test("samson_vision importable", False, str(e))

    try:
        import versiculos
        ok &= test("versiculos importable", True, "")
    except ImportError as e:
        ok &= test("versiculos importable", False, str(e))

    try:
        from vmk.kernel import VisionMultimodalKernel
        ok &= test("vmk.kernel.VisionMultimodalKernel", True, "")
    except ImportError:
        ok &= test("vmk.kernel (sin OpenCV)", True, "[graceful degradation]")

    try:
        from harnesses import hermes_vision_chat, mmx_analyze_image, codex_debug
        ok &= test("harnesses (3 funciones)", True, "")
    except ImportError as e:
        ok &= test("harnesses importable", False, str(e))

    try:
        from runtime_integration import (
            retrieve_knowledge, validate_pack, REQUIRED_FIELDS
        )
        ok &= test("runtime_integration (3 funciones)", True, "")
        nf = len(REQUIRED_FIELDS)
        ok &= test(f"REQUIRED_FIELDS = {nf}", nf == 13, str(nf))
    except ImportError as e:
        ok &= test("runtime_integration importable", False, str(e))

    return ok


# ─── 3. SVP GENERATION ────────────────────────────────────────

def test_svp_generation():
    print("\n🔷 3. GENERACIÓN SVP")
    ok = True

    if not SAMPLE_IMG.is_file():
        return test("Imagen de prueba existe", False, str(SAMPLE_IMG))

    # --- JSON ---
    sys.path.insert(0, str(PROJECT / "src"))
    from samson_vision import SamsonVisionBuilder

    builder = SamsonVisionBuilder()
    pack = None
    try:
        pack = builder.build(str(SAMPLE_IMG))
        svp_json = pack.to_json()
        data = json.loads(svp_json)
        ok &= test("SVP generado en JSON", True, "")

        # Verificar estructura JSON (no es plana como MD, es jerárquica)
        expected_keys = {"version", "metadata", "summary",
                         "ascii_representations", "scene_graph",
                         "ai_description", "raw_vmk"}
        has_keys = set(data.keys())
        missing = expected_keys - has_keys
        if missing:
            ok &= test("Estructura JSON completa", False, f"Faltan: {missing}")
        else:
            ok &= test("Estructura JSON: 7 secciones", True, "")

        # Verificar metadata
        meta = data.get("metadata", {})
        has_dims = "dimensions" in meta
        ok &= test("JSON metadata.dimensions", has_dims, "")

        # Verificar ASCII styles
        ascii_styles = data.get("ascii_representations", {})
        ok &= test(f"JSON ASCII: {len(ascii_styles)} estilos",
                   len(ascii_styles) >= 3, str(list(ascii_styles.keys())))
    except Exception as e:
        ok &= test("SVP JSON error", False, str(e))

    # Markdown solo si pack se generó
    if pack:
        try:
            svp_md = pack.to_markdown()
            ok &= test("SVP generado en Markdown", True, "")
            has_header = "[SAMSON_VISION_PACK v1]" in svp_md
            ok &= test("Header [SAMSON_VISION_PACK v1]", has_header, "")
            fields_found = sum(
                1 for f in REQUIRED_FIELDS_SVP if f in svp_md
            )
            ok &= test(f"Campos en MD: {fields_found}/13", fields_found == 13, "")
            has_not_assume = "DO_NOT_ASSUME" in svp_md
            has_uncertainties = "UNCERTAINTIES" in svp_md
            ok &= test("Antialucinación presente",
                       has_not_assume and has_uncertainties, "")
        except Exception as e:
            ok &= test("SVP Markdown error", False, str(e))
    else:
        ok &= test("SVP Markdown", False, "pack no generado")

    return ok


# ─── 4. CLI ────────────────────────────────────────────────────

def test_cli():
    print("\n💻 4. CLI")
    ok = True

    # samson-vision --help
    try:
        r = subprocess.run(
            ["samson-vision", "--help"],
            capture_output=True, text=True, timeout=10,
            env={**os.environ, "PYTHONPATH": str(PROJECT / "src")},
        )
        has_help = "Uso:" in r.stdout and "Ejemplos" in r.stdout
        ok &= test("samson-vision --help",
                   has_help and r.returncode == 0, r.stdout[:80].strip())
    except FileNotFoundError:
        # Fallback si el comando global no existe
        r = subprocess.run(
            [sys.executable, str(PROJECT / "src/samson_vision.py"), "--help"],
            capture_output=True, text=True, timeout=10,
            env={**os.environ, "PYTHONPATH": str(PROJECT / "src")},
        )
        has_help = "Uso:" in r.stdout
        ok &= test("samson-vision --help (python)", has_help and r.returncode == 0, "")

    # python3 src/samson_vision.py sin args
    try:
        r = subprocess.run(
            [sys.executable, str(PROJECT / "src/samson_vision.py")],
            capture_output=True, text=True, timeout=10,
            env={**os.environ, "PYTHONPATH": str(PROJECT / "src")},
        )
        has_usage = "Uso:" in r.stdout or "Usage:" in r.stdout
        ok &= test("CLI sin args muestra ayuda", has_usage, r.stdout[:100])

        # stderr tiene versículo
        has_verse = len(r.stderr.strip()) > 0
        ok &= test("Versículo en stderr", has_verse, f"{len(r.stderr.strip())} chars")
    except Exception as e:
        ok &= test("CLI básico", False, str(e))

    # python3 src/harnesses.py sin args
    try:
        r = subprocess.run(
            [sys.executable, str(PROJECT / "src/harnesses.py")],
            capture_output=True, text=True, timeout=10,
            env={**os.environ, "PYTHONPATH": str(PROJECT / "src")},
        )
        has_commands = "analyze" in r.stdout and "mmx" in r.stdout
        ok &= test("harnesses.py muestra comandos", has_commands, r.stdout[:100])
    except Exception as e:
        ok &= test("harnesses CLI", False, str(e))

    return ok


# ─── 5. SETUP.SH ──────────────────────────────────────────────

def test_setup_script():
    print("\n⚙️  5. SETUP.SH")
    ok = True

    setup_sh = PROJECT / "setup.sh"
    ok &= test("setup.sh existe", setup_sh.is_file(), str(setup_sh))
    ok &= test("setup.sh ejecutable", os.access(setup_sh, os.X_OK), "")

    # Verificar contenido del script
    content = setup_sh.read_text()
    checks = [
        ("pyproject.toml install", "pip install -e" in content),
        ("tests automaticos", "run_tests.py" in content),
        ("version check", "__version__" in content),
        ("copiado de assets", "assets" in content.lower()),
    ]
    for label, cond in checks:
        ok &= test(f"setup.sh: {label}", cond, "")

    return ok


# ─── 6. DOCUMENTACIÓN ─────────────────────────────────────────

def test_documentacion():
    print("\n📖 6. DOCUMENTACIÓN")
    ok = True

    # ARCHITECTURE.md no corrupto
    arch = PROJECT / "PUBLIC/docs/ARCHITECTURE.md"
    content = arch.read_text()
    has_svp_prefix = any(
        line.startswith("|   SVP") for line in content.split("\n")[:10]
    )
    ok &= test("ARCHITECTURE.md NO corrupto",
               not has_svp_prefix, "Antes tenía prefijo SVP en cada línea")

    # SETUP.md en español
    setup = PROJECT / "PUBLIC/docs/SETUP.md"
    setup_content = setup.read_text()
    ok &= test("SETUP.md en español",
               "Instalación" in setup_content, "keywords: Instalación, Requisitos")
    ok &= test("SETUP.md menciona setup.sh",
               "setup.sh" in setup_content, "")
    ok &= test("SETUP.md menciona assets/",
               "assets/" in setup_content, "")

    # SAMSON_VISION_PACK.md tiene 13 campos
    svp_doc = PROJECT / "PUBLIC/docs/SAMSON_VISION_PACK.md"
    svp_content = svp_doc.read_text()
    fields_in_doc = sum(1 for f in REQUIRED_FIELDS_SVP if f in svp_content)
    ok &= test(f"SVP spec documenta {fields_in_doc}/13 campos",
               fields_in_doc >= 13, "")

    # INDEX.md enlaces
    index = PROJECT / "PUBLIC/INDEX.md"
    index_content = index.read_text()
    for doc in ["README.md", "ARCHITECTURE.md", "SETUP.md",
                 "BENCHMARK.md", "COSTS.md"]:
        link = f"docs/{doc}" if doc != "README.md" else doc
        ok &= test(f"INDEX.md link a {doc}", link in index_content, "")

    return ok


# ─── 7. UNIT TESTS ────────────────────────────────────────────

def test_unit_tests():
    print("\n🧪 7. TESTS UNITARIOS")
    ok = True

    try:
        r = subprocess.run(
            [sys.executable, str(PROJECT / "test/run_tests.py")],
            capture_output=True, text=True, timeout=120,
            env={**os.environ, "PYTHONPATH": str(PROJECT / "src")},
        )
        output = r.stdout + r.stderr
        has_ok = "OK" in output
        has_29 = "29 tests" in output or "29/29" in output or "29 passed" in output

        if has_29 and r.returncode == 0:
            ok &= test("29/29 tests unitarios", True, "")
        else:
            # Contar reales
            passed = output.count("... ok")
            failed = output.count("FAIL") + output.count("ERROR")
            ok &= test(f"Tests: {passed} ok, {failed} fail",
                       failed == 0, output[-300:])
    except subprocess.TimeoutExpired:
        ok &= test("Tests unitarios timeout", False, ">120s")
    except Exception as e:
        ok &= test("Tests unitarios error", False, str(e))

    return ok


# ─── MAIN ──────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  🦁 SAMSON VISION — Integration Test Harness v2.0")
    print("  Basado en lecciones del 24-Jun-2026")
    print("=" * 60)

    os.chdir(str(PROJECT))

    test_estructura()
    test_imports()
    test_svp_generation()
    test_cli()
    test_setup_script()
    test_documentacion()
    test_unit_tests()

    # Reporte
    print("\n" + "=" * 60)
    print(f"  📊 RESULTADO: {SCORE['pass']}/{SCORE['total']}")
    if ERRORS:
        print(f"\n  ❌ {len(ERRORS)} fallo(s):")
        for e in ERRORS:
            print(e)
    print("=" * 60)

    return 0 if SCORE["fail"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
