#!/usr/bin/env python3
"""
samson_core.py — 🦁 Samson Vision Core Engine

Convierte imágenes a ASCII art y patrones de texto que forman un
"lenguaje visual". Un modelo de texto puede "ver" la imagen a través
de estas representaciones y resolver problemas visuales.

Estilos:
  - standard: densidad clásica (@%#*+=-:. )
  - detail: densidad extendida (más niveles de gris)
  - block: bloques unicode (██▄▀)
  - edge: detección de bordes + ASCII
  - color: colores ANSI + ASCII
  - dither: Floyd-Steinberg dithering
  - fanart: variaciones creativas (densidad invertida, patrones)
  - braille: patrones Braille unicode (⣿⣧⣄)
"""
from PIL import Image
import numpy as np
import io
import base64

# ─── Version ──────────────────────────────────────────────

__version__ = "2.0"


# ─── Paletas ASCII ──────────────────────────────────────────────

# Standard: 10 niveles de densidad
PALETTE_STANDARD = "@%#*+=-:. "

# Detail: 16 niveles para más precisión
PALETTE_DETAIL = "@%#&WMHBQRO0kLJYj2t{xv?+*^~=-:.`' "

# Block unicode
PALETTE_BLOCK = ["█", "▓", "▒", "░", " "]

# Simple binaria
PALETTE_BINARY = ["█", " "]

# Braille patterns (4x2 dots)
BRAILLE_BASE = 0x2800

# ─── Funciones core ─────────────────────────────────────────────

def pil_to_array(img):
    """Convierte PIL Image a numpy array."""
    return np.array(img)

def to_grayscale(img):
    """Convierte a escala de grises."""
    if img.mode == 'RGBA':
        # Fondo blanco para alpha
        bg = Image.new('RGB', img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3])
        img = bg
    return img.convert('L')

def resize_for_ascii(img, max_width=80, max_height=60):
    """Redimensiona manteniendo aspect ratio.
    Los caracteres ASCII son ~2x más altos que anchos, así que
    ajustamos el aspect ratio para que la imagen se vea proporcionada.
    """
    w, h = img.size
    # Ajuste de aspect ratio para caracteres (ancho:alto ≈ 1:2)
    aspect = w / h
    ascii_width = max_width
    ascii_height = min(int(ascii_width / (aspect * 0.5)), max_height)
    
    if ascii_height > max_height:
        ascii_height = max_height
        ascii_width = min(int(ascii_height * aspect * 0.5), max_width)
    
    return img.resize((ascii_width, ascii_height), Image.LANCZOS)

# ─── Convertidores por estilo ───────────────────────────────────

def _ascii_from_array(arr, palette):
    """Convierte array numpy a ASCII con auto-stretch de contraste."""
    arr = arr.astype(float)
    lo, hi = arr.min(), arr.max()
    if hi - lo > 5:
        arr = (arr - lo) / (hi - lo) * 255
    arr = np.clip(arr, 0, 255)
    indices = (arr * (len(palette) - 1) / 255.0).astype(int)
    lines = []
    for row in indices:
        line = "".join(palette[i] for i in row)
        lines.append(line)
    return "\n".join(lines)

def to_ascii_standard(img, width=80, height=60):
    """ASCII clásico por densidad de gris con auto-stretch de contraste."""
    img = resize_for_ascii(to_grayscale(img), width, height)
    return _ascii_from_array(np.array(img), PALETTE_STANDARD)

def to_ascii_detail(img, width=80, height=60):
    """ASCII con paleta extendida + auto-stretch."""
    img = resize_for_ascii(to_grayscale(img), width, height)
    return _ascii_from_array(np.array(img), PALETTE_DETAIL)

def to_ascii_block(img, width=80, height=60):
    """Usa bloques unicode █▓▒░ con auto-stretch."""
    img = resize_for_ascii(to_grayscale(img), width, height)
    return _ascii_from_array(np.array(img), PALETTE_BLOCK)

def to_ascii_edge(img, width=80, height=60):
    """Detección de bordes + ASCII (resalta contornos)."""
    img_gray = to_grayscale(img)
    img_gray = resize_for_ascii(img_gray, width, height)
    arr = np.array(img_gray, dtype=float)
    
    # Sobel simple para detectar bordes
    gx = np.abs(np.diff(arr, axis=1, append=0))
    gy = np.abs(np.diff(arr, axis=0, append=0))
    edges = np.sqrt(gx**2 + gy**2)
    edges = np.clip(edges, 0, 255)
    
    # Invertir: bordes = oscuro, fondo = claro
    edges = 255 - edges
    
    return _ascii_from_array(edges, PALETTE_STANDARD)

def to_ascii_dither(img, width=80, height=60):
    """ASCII con Floyd-Steinberg dithering para mejor gradiente."""
    img = resize_for_ascii(to_grayscale(img), width, height)
    arr = np.array(img, dtype=float)
    h, w = arr.shape
    
    # Auto-stretch primero
    lo, hi = arr.min(), arr.max()
    if hi - lo > 5:
        arr = (arr - lo) / (hi - lo) * 255
    arr = np.clip(arr, 0, 255)
    
    # Floyd-Steinberg dithering
    for y in range(h):
        for x in range(w):
            old = arr[y, x]
            new = round(old / 255) * 255
            arr[y, x] = new
            error = old - new
            if x + 1 < w:
                arr[y, x+1] += error * 7 / 16
            if y + 1 < h:
                if x > 0:
                    arr[y+1, x-1] += error * 3 / 16
                arr[y+1, x] += error * 5 / 16
                if x + 1 < w:
                    arr[y+1, x+1] += error * 1 / 16
    
    return _ascii_from_array(arr, PALETTE_BINARY)

def to_ascii_fanart(img, width=80, height=60):
    """Versión creativa con símbolos variados."""
    img = resize_for_ascii(to_grayscale(img), width, height)
    fanart_chars = list("●◉◎○◐◑◒◓▒▓")
    return _ascii_from_array(np.array(img), fanart_chars)

def to_ascii_braille(img, width=80, height=60):
    """Patrones Braille unicode para máxima densidad."""
    img = resize_for_ascii(to_grayscale(img), width * 2, height * 4)
    img_gray = to_grayscale(img)
    arr = np.array(img_gray)
    h, w = arr.shape
    
    # Asegurar dimensiones pares para agrupar en bloques 2x4
    h = h - (h % 4)
    w = w - (w % 2)
    arr = arr[:h, :w]
    
    lines = []
    for by in range(0, h, 4):
        line = ""
        for bx in range(0, w, 2):
            block = arr[by:by+4, bx:bx+2]
            avg = np.mean(block)
            # Mapear a patrón braille
            intensity = avg / 255.0
            pattern = int(intensity * 255)
            # Crear patrón braille
            braille = BRAILLE_BASE
            dots = [
                (0, 0), (0, 1), (0, 2), (1, 0),
                (1, 1), (1, 2), (0, 3), (1, 3)
            ]
            for i, (dy, dx) in enumerate(dots):
                if by + dy < h and bx + dx < w:
                    if arr[by + dy, bx + dx] < 128:  # oscuro = punto activo
                        braille |= (1 << i)
            line += chr(braille)
        lines.append(line)
    return "\n".join(lines)

def to_ascii_color(img, width=80, height=60):
    """ASCII con códigos de color ANSI."""
    img_rgb = img.convert('RGB')
    img_gray = to_grayscale(img)
    img_rgb = resize_for_ascii(img_rgb, width, height)
    img_gray = resize_for_ascii(img_gray, width, height)
    
    arr_rgb = np.array(img_rgb)
    arr_gray = np.array(img_gray)
    
    indices = (arr_gray * (len(PALETTE_STANDARD) - 1) / 255).astype(int)
    
    lines = []
    for y in range(arr_gray.shape[0]):
        line = ""
        for x in range(arr_gray.shape[1]):
            r, g, b = arr_rgb[y, x]
            char = PALETTE_STANDARD[indices[y, x]]
            # ANSI true color
            line += f"\033[38;2;{r};{g};{b}m{char}\033[0m"
        lines.append(line)
    return "\n".join(lines)

# ─── Convertidor unificado ──────────────────────────────────────

STYLE_REGISTRY = {
    "standard": to_ascii_standard,
    "detail": to_ascii_detail,
    "block": to_ascii_block,
    "edge": to_ascii_edge,
    "dither": to_ascii_dither,
    "fanart": to_ascii_fanart,
    "braille": to_ascii_braille,
    "color": to_ascii_color,
}

def convert_image(image_input, style="standard", width=80, height=60):
    """
    Convierte una imagen a ASCII art.
    
    Args:
        image_input: PIL Image, ruta a archivo, o bytes
        style: Estilo de ASCII (standard, detail, block, edge, dither, fanart, braille, color)
        width: Ancho máximo en caracteres
        height: Alto máximo en caracteres
    
    Returns:
        String con el ASCII art
    """
    if isinstance(image_input, str):
        img = Image.open(image_input)
    elif isinstance(image_input, bytes):
        img = Image.open(io.BytesIO(image_input))
    elif isinstance(image_input, Image.Image):
        img = image_input
    else:
        raise ValueError(f"Tipo no soportado: {type(image_input)}")
    
    converter = STYLE_REGISTRY.get(style)
    if not converter:
        styles = ", ".join(STYLE_REGISTRY.keys())
        raise ValueError(f"Estilo '{style}' no válido. Estilos: {styles}")
    
    return converter(img, width, height)

def convert_all_styles(image_input, width=80, height=60):
    """Convierte una imagen a todos los estilos y devuelve dict."""
    if isinstance(image_input, str):
        img = Image.open(image_input)
    elif isinstance(image_input, bytes):
        img = Image.open(io.BytesIO(image_input))
    elif isinstance(image_input, Image.Image):
        img = image_input
    else:
        raise ValueError(f"Tipo no soportado: {type(image_input)}")
    
    result = {}
    for name, converter in STYLE_REGISTRY.items():
        if name != "color":  # color usa ANSI, no es texto plano
            try:
                result[name] = converter(img.copy(), width, height)
            except Exception as e:
                result[name] = f"[ERROR: {e}]"
    return result

# ─── Patrón de Lenguaje Visual ─────────────────────────────────

def create_visual_language(image_input, width=40, height=30):
    """
    Crea una representación multi-capa de la imagen como "lenguaje visual".
    Combina múltiples estilos ASCII + metadatos para que un modelo
    pueda "ver" la imagen completa a través del texto.
    """
    if isinstance(image_input, str):
        img = Image.open(image_input)
    elif isinstance(image_input, bytes):
        img = Image.open(io.BytesIO(image_input))
    elif isinstance(image_input, Image.Image):
        img = image_input
    else:
        raise ValueError(f"Tipo no soportado: {type(image_input)}")
    
    img_gray = to_grayscale(img)
    img_rgb = img.convert('RGB')
    
    # Información básica
    w, h = img.size
    aspect_ratio = w / h
    
    # Analizar imagen
    arr_gray = np.array(resize_for_ascii(img_gray, 40, 30))
    arr_rgb = np.array(resize_for_ascii(img_rgb, 40, 30))
    
    # Estadísticas de color
    avg_color = tuple(int(x) for x in arr_rgb.mean(axis=(0, 1)))
    brightness = int(arr_gray.mean())
    contrast = int(arr_gray.std())
    
    # Paleta de colores dominantes (simple: cuantizar)
    flat = arr_rgb.reshape(-1, 3)
    # Muestrear cada N píxel por velocidad
    sampled = flat[::10]
    # Colores únicos redondeados
    quantized = (sampled // 64) * 64 + 32
    unique_colors = set(tuple(int(c) for c in row) for row in quantized)
    sorted_colors = sorted(unique_colors, 
                          key=lambda c: -np.sum((np.array(c) - np.array(avg_color))**2))
    top_colors = sorted_colors[:8]
    
    # Construir lenguaje visual multicapa
    layers = []
    
    # Capa 1: Vista general (standard, compacto)
    ascii_std = to_ascii_standard(img.copy(), width=40, height=25)
    layers.append(f"[STANDARD ASCII - Vista general]\n{ascii_std}")
    
    # Capa 2: Bordes y contornos
    ascii_edge = to_ascii_edge(img.copy(), width=40, height=25)
    layers.append(f"[EDGE DETECTION - Bordes y contornos]\n{ascii_edge}")
    
    # Capa 3: Detalle fino
    ascii_detail = to_ascii_detail(img.copy(), width=40, height=25)
    layers.append(f"[DETAIL - Detalle fino]\n{ascii_detail}")
    
    # Capa 4: Bloques (más densidad visual)
    ascii_block = to_ascii_block(img.copy(), width=40, height=25)
    layers.append(f"[BLOCK UNICODE - Densidad]\n{ascii_block}")
    
    # Capa 5: Patrón creativo
    ascii_fanart = to_ascii_fanart(img.copy(), width=40, height=25)
    layers.append(f"[FANART - Patrones creativos]\n{ascii_fanart}")
    
    # Metadatos
    metadata = (
        f"=== METADATOS DE LA IMAGEN ===\n"
        f"Dimensiones originales: {w}x{h}\n"
        f"Aspect ratio: {aspect_ratio:.2f}\n"
        f"Brillo medio: {brightness:.0f}/255\n"
        f"Contraste: {contrast:.0f}/255\n"
        f"Color dominante: RGB{tuple(avg_color)}\n"
        f"Colores principales: {', '.join(f'RGB{c}' for c in top_colors[:5])}\n"
        f"Perfil de brillo: {'Alto' if brightness > 170 else 'Medio' if brightness > 85 else 'Bajo'}\n"
        f"Contraste: {'Alto' if contrast > 60 else 'Medio' if contrast > 30 else 'Bajo'}\n"
    )
    
    # Ensamblar lenguaje visual completo
    visual_language = (
        f"🦁 SAMSON VISUAL LANGUAGE\n"
        f"{'=' * 50}\n\n"
        f"{metadata}\n"
        f"{'=' * 50}\n"
        f"REPRESENTACIONES ASCII (multi-capa):\n\n"
        f"{chr(10).join(layers)}\n\n"
        f"{'=' * 50}\n"
        f"INSTRUCCIONES: Las representaciones ASCII arriba codifican\n"
        f"la imagen completa en texto. Cada capa muestra un aspecto\n"
        f"diferente. Usa esta información para entender la imagen y\n"
        f"responder preguntas sobre ella.\n"
    )
    
    return visual_language

# ─── Test rápido ────────────────────────────────────────────────

def test_core():
    """Test básico del core engine."""
    # Crear imagen de prueba
    img = Image.new('RGB', (100, 50), (30, 30, 50))
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    draw.rectangle([10, 10, 50, 40], fill=(200, 100, 50))
    draw.ellipse([60, 10, 90, 40], fill=(50, 150, 200))
    draw.text((15, 20), "SV", fill=(255, 255, 255))
    
    print("🦁 SAMSON VISION CORE TEST")
    print("=" * 50)
    
    # Probar todos los estilos
    for name, converter in STYLE_REGISTRY.items():
        if name == "color":
            continue  # ANSI colors, skip
        try:
            result = converter(img.copy(), width=60, height=30)
            print(f"\n[{name.upper()}]\n{result[:200]}...")
        except Exception as e:
            print(f"\n[{name.upper()}] ERROR: {e}")
    
    # Probar lenguaje visual
    print("\n" + "=" * 50)
    print("VISUAL LANGUAGE:")
    vl = create_visual_language(img, width=40, height=20)
    print(vl[:500] + "...\n")
    print("✅ Core engine OK")

if __name__ == "__main__":
    # Marca espiritual — la visión de Sansón era el plan de Dios
    try:
        from versiculos import imprimir
        imprimir()
    except ImportError:
        pass
    test_core()
