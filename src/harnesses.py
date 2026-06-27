"""
🦁 Harnesses — Arneses de integración para Samson Vision.

Conectores para:
  1. Hermes Agent (perfil "vision")
  2. MiniMax M3 (multimodal vía mmx CLI)
  3. Codex CLI (debugging y razonamiento)
  4. API unificada
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional


# ─── Paths ─────────────────────────────────────────────────────

_PKG_ROOT = Path(__file__).resolve().parent.parent
PROJECT_DIR = os.environ.get("SAMSON_VISION_HOME", str(_PKG_ROOT))
SRC_DIR = os.path.join(PROJECT_DIR, "src")
SAMSON_DIR = os.path.expanduser("~/.hermes/samson-vision")
LOG_DIR = os.path.expanduser("~/.hermes/logs")
HERMES_PROFILE_DIR = os.path.expanduser("~/.hermes/profiles/vision")


# ─── Hermes Harness ────────────────────────────────────────────

def hermes_vision_chat(query: str, image_path: Optional[str] = None) -> str:
    """
    Usa Samson Vision desde el perfil 'vision' de Hermes.
    
    Args:
        query: Pregunta sobre la imagen
        image_path: Ruta a la imagen (opcional)
    
    Returns:
        Respuesta del análisis
    """
    cmd = ["hermes", "-s", "samson-vision", "chat", "-q"]
    
    if image_path:
        full_query = f"{query} (imagen: {image_path})"
    else:
        full_query = query
    
    cmd.append(full_query)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return result.stdout if result.returncode == 0 else result.stderr


# ─── MiniMax M3 Harness ───────────────────────────────────────

def mmx_analyze_image(image_path: str, prompt: str = "Describe esta imagen") -> str:
    """
    Envía una imagen a MiniMax M3 para análisis multimodal.
    Usa `mmx vision describe` para obtener descripción.
    
    Args:
        image_path: Ruta a la imagen
        prompt: Prompt opcional
    
    Returns:
        Descripción del modelo
    """
    mmx = _find_mmx()
    if not mmx:
        return "[ERROR: mmx CLI no encontrado]"
    
    try:
        # Asegurar export PATH para mmx
        env = os.environ.copy()
        env["PATH"] = "/home/linuxbrew/.linuxbrew/bin:" + env.get("PATH", "")
        
        result = subprocess.run(
            [mmx, "vision", "describe", "--image", image_path,
             "--question", prompt, "--output", "text"],
            capture_output=True, text=True, timeout=120, env=env
        )
        output = result.stdout.strip() or result.stderr.strip()
        return output
    except subprocess.TimeoutExpired:
        return "[ERROR: Timeout en mmx vision describe]"
    except Exception as e:
        return f"[ERROR: {e}]"


def mmx_samson_analysis(image_path: str) -> dict:
    """
    Análisis dual: Samson Vision (ASCII) + MiniMax M3 (multimodal).
    
    Returns:
        Dict con análisis de ambos sistemas
    """
    # Importar aquí para evitar circular imports
    sys.path.insert(0, SRC_DIR)
    
    from samson_core import create_visual_language, convert_image
    from PIL import Image
    
    try:
        img = Image.open(image_path)
    except Exception as e:
        return {"error": f"No se pudo abrir {image_path}: {e}"}
    
    # Samson Vision: lenguaje visual ASCII
    sv_analysis = create_visual_language(img, width=60, height=40)
    
    # MiniMax M3: análisis multimodal
    mmx_result = mmx_analyze_image(image_path)
    
    return {
        "samson_vision_ascii": sv_analysis,
        "minimax_m3_analysis": mmx_result,
        "dual_verdict": (
            "Samson Vision proporciona representación espacial estructurada;\n"
            "MiniMax M3 aporta comprensión semántica nativa.\n"
            "Juntos ofrecen una visión completa: forma + significado."
        ),
    }


def _find_mmx() -> Optional[str]:
    """Busca el binario mmx en rutas conocidas."""
    candidates = [
        "/home/linuxbrew/.linuxbrew/bin/mmx",
        "/usr/local/bin/mmx",
        "mmx",  # PATH lookup
    ]
    for c in candidates:
        try:
            subprocess.run([c, "--version"], capture_output=True, timeout=5)
            return c
        except (FileNotFoundError, PermissionError):
            continue
    return None


# ─── Codex Harness ─────────────────────────────────────────────

def codex_debug(context: str, question: str) -> str:
    """
    Consulta a Codex CLI para debugging y razonamiento.
    
    Args:
        context: Contexto del problema (errores, logs, código)
        question: Pregunta específica
    
    Returns:
        Respuesta de Codex
    """
    codex = _find_codex()
    if not codex:
        return "[ERROR: codex CLI no encontrado]"
    
    full_prompt = f"Contexto:\n{context}\n\nPregunta: {question}"
    
    try:
        result = subprocess.run(
            [codex, "-z", full_prompt],
            capture_output=True, text=True, timeout=120
        )
        return result.stdout.strip() or result.stderr.strip()
    except subprocess.TimeoutExpired:
        return "[ERROR: Timeout en codex]"
    except Exception as e:
        return f"[ERROR: {e}]"


def _find_codex() -> Optional[str]:
    """Busca el binario codex."""
    candidates = [
        os.path.expanduser("~/.local/bin/codex"),
        "/usr/local/bin/codex",
        "codex",
    ]
    for c in candidates:
        try:
            subprocess.run([c, "-z", "test"], capture_output=True, timeout=10)
            return c
        except (FileNotFoundError, PermissionError, subprocess.TimeoutExpired):
            continue
    return None


# ─── Pipeline de análisis completo ─────────────────────────────

def full_analysis_pipeline(image_path: str, prompt: str = "Describe esta imagen") -> dict:
    """
    Pipeline completo: Samson Vision + VMK + MiniMax M3 + Codex.
    
    Args:
        image_path: Ruta a la imagen
        prompt: Pregunta sobre la imagen
    
    Returns:
        Dict con análisis de todos los sistemas
    """
    from PIL import Image
    
    try:
        img = Image.open(image_path)
    except Exception as e:
        return {"error": str(e)}
    
    # 1. Samson Core
    sys.path.insert(0, SRC_DIR)
    from samson_core import create_visual_language
    
    sv = create_visual_language(img, width=60, height=40)
    
    # 2. VMK
    try:
        from vmk import VisionMultimodalKernel
        vmk = VisionMultimodalKernel()
        r = vmk.process_image(img)
        sg = vmk.get_last_scene_graph()
        vmk_report = sg.to_text() if sg else str(r)
    except Exception as e:
        vmk_report = f"[VMK no disponible: {e}]"
    
    # 3. MiniMax M3
    mmx = mmx_analyze_image(image_path, prompt)
    
    result = {
        "samson_vision": sv,
        "vmk_analysis": vmk_report,
        "minimax_m3": mmx,
    }
    return result


# ─── CLI ───────────────────────────────────────────────────────

def cli():
    """Interfaz CLI unificada."""

    # Marca espiritual — Sansón no vio con sus ojos, su visión era el plan de Dios
    try:
        from versiculos import imprimir
        imprimir()
    except ImportError:
        pass

    if len(sys.argv) < 2:
        print("🦁 Samson Vision — Harnesses CLI")
        print("Uso: python3 harnesses.py <comando> [args]")
        print("\nComandos:")
        print("  analyze <imagen> [prompt]  — Pipeline completo")
        print("  mmx <imagen> [prompt]      — Solo MiniMax M3")
        print("  sv <imagen>                — Solo Samson Vision")
        print("  codex <contexto> <pregunta> — Consultar Codex")
        return

    cmd = sys.argv[1]

    if cmd == "analyze":
        path = sys.argv[2] if len(sys.argv) > 2 else None
        prompt = sys.argv[3] if len(sys.argv) > 3 else "Describe esta imagen"
        if not path:
            print("Uso: harnesses.py analyze <imagen> [prompt]")
            return
        result = full_analysis_pipeline(path, prompt)
        for k, v in result.items():
            print(f"\n{'=' * 60}")
            print(f"  {k.upper()}")
            print(f"{'=' * 60}")
            print(v[:2000])

    elif cmd == "mmx":
        path = sys.argv[2] if len(sys.argv) > 2 else None
        prompt = sys.argv[3] if len(sys.argv) > 3 else "Describe esta imagen"
        if not path:
            print("Uso: harnesses.py mmx <imagen> [prompt]")
            return
        result = mmx_analyze_image(path, prompt)
        print(result)

    elif cmd == "sv":
        path = sys.argv[2] if len(sys.argv) > 2 else None
        if not path:
            print("Uso: harnesses.py sv <imagen>")
            return
        result = full_analysis_pipeline(path)
        print(result.get("samson_vision", "Error"))

    elif cmd == "codex":
        context = sys.argv[2] if len(sys.argv) > 2 else ""
        question = sys.argv[3] if len(sys.argv) > 3 else "¿Qué ves?"
        if not context:
            print("Uso: harnesses.py codex <contexto> <pregunta>")
            return
        result = codex_debug(context, question)
        print(result)


if __name__ == "__main__":
    cli()
