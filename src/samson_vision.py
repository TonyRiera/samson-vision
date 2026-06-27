"""
🦁 Samson Vision Pack — Formato unificado de salida visual→texto.

Transforma el análisis de Samson Vision (Core + VMK + OCR + color) en un
paquete textual multi-capa optimizado para que una IA sin visión pueda
interpretar la imagen con la máxima fidelidad posible.

El formato incluye:
  1. Metadatos (dimensiones, tipo de imagen, calidad)
  2. Resumen visual (descripción global)
  3. Mapa ASCII multi-estilo
  4. Coordenadas normalizadas (0-100) de elementos detectados
  5. Jerarquía visual (niveles 1-5 de importancia)
  6. Mapa de densidad visual (grid 10x10)
  7. OCR con coordenadas (texto detectado y su posición)
  8. Objetos detectados con bounding boxes normalizados
  9. Paleta de colores textual (blue_dark, red_medium, etc.)
  10. HTML visual simplificado (layout + semántica)
  11. Versión para IA sin visión (instrucciones de interpretación)
  12. Scene graph completo
"""
import io
import json
import base64
import logging
from dataclasses import dataclass, field, asdict
from typing import Optional
from enum import Enum
from PIL import Image
import numpy as np

logger = logging.getLogger("samson_vision")



SVP_SCHEMA_VERSION = "1.0"

def _package_version() -> str:
    try:
        from importlib.metadata import version as pkg_version
        return pkg_version("samson-vision")
    except Exception:
        return "0.3.2"

PACKAGE_VERSION = _package_version()

# ═══════════════════════════════════════════════════════════════
#  SCHEMA / DATA CLASSES
# ═══════════════════════════════════════════════════════════════

class MotionPattern(str, Enum):
    STATIC = "STATIC"
    BLINK = "BLINK"
    SLIDE_LEFT = "SLIDE_LEFT"
    SLIDE_RIGHT = "SLIDE_RIGHT"
    SLIDE_UP = "SLIDE_UP"
    SLIDE_DOWN = "SLIDE_DOWN"
    ZOOM_IN = "ZOOM_IN"
    ZOOM_OUT = "ZOOM_OUT"
    FADE = "FADE"
    LOADER = "LOADER"
    CAROUSEL = "CAROUSEL"
    SCROLL_Y = "SCROLL_Y"
    STICKY = "STICKY"
    UNKNOWN = "UNKNOWN"


@dataclass
class BBox:
    """Bounding box con coordenadas normalizadas (0-100)."""
    x1: float  # 0-100 (% desde borde izquierdo)
    y1: float  # 0-100 (% desde borde superior)
    x2: float
    y2: float

    def __post_init__(self):
        for attr in ['x1', 'y1', 'x2', 'y2']:
            val = getattr(self, attr)
            setattr(self, attr, round(max(0, min(100, val)), 1))

    @property
    def width(self) -> float:
        return round(self.x2 - self.x1, 1)

    @property
    def height(self) -> float:
        return round(self.y2 - self.y1, 1)

    @property
    def center(self) -> tuple:
        return (round((self.x1 + self.x2) / 2, 1),
                round((self.y1 + self.y2) / 2, 1))

    @property
    def area_pct(self) -> float:
        return round(self.width * self.height / 100, 1)

    def to_dict(self) -> dict:
        return {"x1": self.x1, "y1": self.y1, "x2": self.x2, "y2": self.y2,
                "w": self.width, "h": self.height, "cx": self.center[0],
                "cy": self.center[1], "area_pct": self.area_pct}

    @staticmethod
    def from_pixels(x0, y0, x1, y1, img_w, img_h):
        """Crea BBox desde coordenadas de píxeles."""
        return BBox(
            round(x0 / img_w * 100, 1), round(y0 / img_h * 100, 1),
            round(x1 / img_w * 100, 1), round(y1 / img_h * 100, 1)
        )


@dataclass
class DetectedObject:
    """Objeto detectado en la imagen."""
    label: str
    bbox: BBox
    confidence: float = 0.0
    hierarchy_level: int = 3  # 1=principal, 2=secundario, 3=detalle
    attributes: dict = field(default_factory=dict)


@dataclass
class DetectedText:
    """Texto detectado (OCR) con coordenadas."""
    text: str
    bbox: BBox
    confidence: float = 0.0
    language: str = ""


@dataclass
class ColorInfo:
    """Color con nombre textual."""
    hex: str = ""
    name: str = ""  # blue_dark, red_medium, etc.
    percentage: float = 0.0
    bbox: Optional[BBox] = None

    def to_dict(self) -> dict:
        return {"hex": self.hex, "name": self.name,
                "percentage": self.percentage}


@dataclass
class MotionInfo:
    pattern: MotionPattern = MotionPattern.STATIC
    start_bbox: Optional[BBox] = None
    end_bbox: Optional[BBox] = None
    velocity: float = 0.0
    frames_analyzed: int = 0


@dataclass
class SceneGraphSimplified:
    """Scene Graph simplificado para el pack."""
    objects: list = field(default_factory=list)
    text_elements: list = field(default_factory=list)
    color_palette: list = field(default_factory=list)
    density_map: list = field(default_factory=list)  # grid 10x10
    hierarchy: dict = field(default_factory=dict)  # {level: [labels]}
    image_dimensions: str = ""
    aspect_ratio: float = 0.0


@dataclass
class AIDescription:
    """Versión para IA sin visión — instrucciones de interpretación."""
    summary: str = ""
    spatial_layout: str = ""
    important_elements: list = field(default_factory=list)
    colors_present: list = field(default_factory=list)
    motion_summary: str = ""
    suggested_focus: Optional[BBox] = None
    html_visual: str = ""
    interpretation_instructions: str = ""


@dataclass
class SamsonVisionPack:
    """Paquete completo de vision textual para IA."""
    version: str = SVP_SCHEMA_VERSION
    
    # Metadata
    metadata: dict = field(default_factory=dict)
    
    # Resumen
    summary: dict = field(default_factory=dict)
    
    # Representaciones ASCII
    ascii_representations: dict = field(default_factory=dict)
    
    # Análisis
    scene_graph: Optional[SceneGraphSimplified] = None
    
    # Descripción para IA
    ai_description: Optional[AIDescription] = None
    
    # Debug / raw data
    raw_vmk: dict = field(default_factory=dict)

    def to_json(self, indent=2) -> str:
        """Serializa a JSON."""
        return json.dumps(self, default=lambda o: o.to_dict() if hasattr(o, 'to_dict') else asdict(o),
                          indent=indent, ensure_ascii=False)

    def to_markdown(self) -> str:
        """Genera markdown del Samson Vision Pack siguiendo el schema v1."""
        lines = []
        m = self.metadata
        s = self.summary
        sg = self.scene_graph
        ai = self.ai_description

        lines.append("[SAMSON_VISION_PACK v1]")
        lines.append("")
        lines.append("IMAGE_TYPE:")
        lines.append(f"- domain: {m.get('domain', 'web')}")
        lines.append(f"- subtype: {m.get('subtype', 'generic')}")
        lines.append(f"- quality: {m.get('quality', 'medium')}")
        lines.append(f"- dimensions: {m.get('dimensions', '?')}")
        lines.append(f"- aspect_ratio: {m.get('aspect_ratio', '?')}")
        lines.append("")

        lines.append("GLOBAL_SUMMARY:")
        lines.append(f"- {s.get('global', 'Sin descripción disponible.')}")
        lines.append("")

        lines.append("VISUAL_HIERARCHY:")
        if sg and sg.objects:
            sorted_objs = sorted(sg.objects, key=lambda o: o.hierarchy_level)
            for obj in sorted_objs[:10]:
                b = obj.bbox
                lines.append(f"- [{b.x1:.0f},{b.y1:.0f},{b.x2:.0f},{b.y2:.0f}] {obj.label} (nivel {obj.hierarchy_level})")
        lines.append("")

        lines.append("LAYOUT_MAP:")
        if sg and sg.objects:
            for obj in sg.objects[:15]:
                b = obj.bbox
                lines.append(f"- [{b.x1:.0f},{b.y1:.0f},{b.x2:.0f},{b.y2:.0f}] {obj.label}")
        lines.append("")

        lines.append("OCR_TEXT:")
        if sg and sg.text_elements:
            for t in sg.text_elements[:30]:
                b = t.bbox
                conf = "high" if t.confidence > 0.8 else "medium" if t.confidence > 0.5 else "low"
                lines.append(f"- \"{t.text}\" at [{b.x1:.0f},{b.y1:.0f},{b.x2:.0f},{b.y2:.0f}], confidence {conf}")
        else:
            lines.append("- (sin OCR disponible)")
        lines.append("")

        lines.append("OBJECTS_AND_COMPONENTS:")
        if sg and sg.objects:
            for obj in sg.objects[:15]:
                b = obj.bbox
                lines.append(f"- {obj.label} at [{b.x1:.0f},{b.y1:.0f},{b.x2:.0f},{b.y2:.0f}], area {b.area_pct:.0f}%")
        lines.append("")

        lines.append("COLOR_MAP:")
        if sg and sg.color_palette:
            for c in sg.color_palette[:6]:
                lines.append(f"- {c.name}: {c.percentage:.0f}%")
        lines.append("")

        lines.append("DENSITY_MAP:")
        if sg and sg.density_map:
            for y, row in enumerate(sg.density_map[:10]):
                avg = sum(row) / len(row) if row else 0
                label = "alta" if avg > 40 else "media" if avg > 15 else "baja"
                lines.append(f"- y={y*10:.0f}%: densidad {label}")
        lines.append("")

        lines.append("ASCII_REPRESENTATION:")
        std = self.ascii_representations.get("standard", "")
        if std:
            # Tomar primeras líneas significativas
            sig_lines = [l for l in std.split("\n") if l.strip()][:6]
            lines.append("```text")
            for l in sig_lines:
                lines.append(l[:80])
            lines.append("```")
        lines.append("")

        lines.append("USER_ACTIONS:")
        if sg and sg.objects:
            # Sugerir centros de objetos como puntos de acción
            for obj in sg.objects[:5]:
                b = obj.bbox
                cx, cy = b.center
                lines.append(f"- Interactuar con {obj.label} around [{cx:.0f},{cy:.0f}]")
        lines.append("")

        lines.append("UNCERTAINTIES:")
        lines.append(f"- La detección de objetos tiene precisión limitada ({m.get('n_objects', 0)} regiones detectadas)")
        if m.get('n_text_elements', 0) == 0:
            lines.append("- No se pudo realizar OCR con alta confianza")
        lines.append("")

        lines.append("DO_NOT_ASSUME:")
        lines.append("- No asumir texto legible donde OCR no lo confirmó")
        lines.append("- No asumir funcionalidad de elementos no etiquetados")
        lines.append("- No asumir contenido fuera del área visible")
        lines.append("")

        lines.append("FINAL_INTERPRETATION_FOR_TEXT_ONLY_AI:")
        if ai and ai.summary:
            lines.append(f"- {ai.summary}")
        if ai and ai.important_elements:
            for elem in ai.important_elements[:3]:
                lines.append(f"- {elem}")
        lines.append("")

        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
#  COLOR NAMING
# ═══════════════════════════════════════════════════════════════

COLOR_NAMES = {
    (0, 0, 0): "black",
    (255, 255, 255): "white",
    (128, 128, 128): "gray_medium",
    (192, 192, 192): "gray_light",
    (64, 64, 64): "gray_dark",
    (240, 240, 240): "gray_very_light",
    (200, 200, 200): "gray_pale",
    (66, 133, 244): "blue_medium",
    (26, 115, 232): "blue_medium_google",
    (52, 168, 83): "green_medium",
    (234, 67, 53): "red_medium",
    (251, 188, 4): "yellow_medium",
    (255, 255, 0): "yellow_bright",
    (255, 0, 0): "red_bright",
    (0, 255, 0): "green_bright",
    (0, 0, 255): "blue_bright",
    (255, 165, 0): "orange_medium",
    (128, 0, 128): "violet_medium",
    (0, 128, 128): "teal_medium",
    (255, 192, 203): "pink_light",
    (165, 42, 42): "brown_medium",
    (245, 245, 245): "gray_off_white",
    (248, 249, 250): "gray_google_bg",
}


def name_color(r, g, b) -> str:
    """Asigna nombre textual a un color RGB."""
    best_name = "unknown"
    best_dist = float("inf")
    for (cr, cg, cb), name in COLOR_NAMES.items():
        dist = (r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2
        if dist < best_dist:
            best_dist = dist
            best_name = name
    if best_dist > 5000:
        # Clasificación genérica
        brightness = (r + g + b) / 3
        if brightness > 230:
            best_name = "white_near"
        elif brightness > 180:
            if r > g + 30: best_name = "red_light"
            elif g > r + 30: best_name = "green_light"
            elif b > r + 30: best_name = "blue_light"
            else: best_name = "gray_light"
        elif brightness > 100:
            if r > g + 30 and r > b + 30: best_name = "red_medium"
            elif g > r + 30 and g > b + 30: best_name = "green_medium"
            elif b > r + 30 and b > g + 30: best_name = "blue_medium"
            else: best_name = "gray_medium"
        else:
            if r > g + 30 and r > b + 30: best_name = "red_dark"
            elif g > r + 30 and g > b + 30: best_name = "green_dark"
            elif b > r + 30 and b > g + 30: best_name = "blue_dark"
            else: best_name = "gray_dark"
    return best_name


# ═══════════════════════════════════════════════════════════════
#  BUILDER
# ═══════════════════════════════════════════════════════════════

class SamsonVisionBuilder:
    """Construye un Samson Vision Pack a partir de una imagen."""

    def __init__(self):
        self._vmk = None
        self._img = None

    def build(self, image_input, prompt: str = "") -> SamsonVisionPack:
        """
        Construye el paquete completo de visión textual.
        
        Args:
            image_input: PIL Image, bytes, ruta, o base64 data URI
            prompt: Pregunta opcional del usuario
        
        Returns:
            SamsonVisionPack con todas las capas
        """
        # Cargar imagen
        self._img = self._load_image(image_input)
        if self._img is None:
            return self._error_pack("No se pudo cargar la imagen")

        img = self._img
        orig_w, orig_h = img.size

        # 1. VMK analysis
        vmk_report = self._run_vmk(img)

        # 2. ASCII representations
        ascii_repr = self._generate_ascii(img)

        # 3. Density map (grid 10x10)
        density_map = self._compute_density(img)

        # 4. Color palette
        color_palette = self._extract_colors(img)

        # 5. Detect text zones (OCR placeholder - will use PaddleOCR if available)
        text_elements = self._detect_text(img)

        # 6. Build scene graph
        sg = self._build_scene_graph(vmk_report, text_elements, color_palette,
                                      density_map, orig_w, orig_h)

        # 7. Determine hierarchy
        hierarchy = self._compute_hierarchy(sg.objects)

        # 8. Build AI description
        ai_desc = self._build_ai_description(
            vmk_report, ascii_repr, sg, hierarchy, prompt
        )

        # 9. Metadata
        metadata = {
            "dimensions": f"{orig_w}x{orig_h}",
            "aspect_ratio": round(orig_w / orig_h, 3) if orig_h > 0 else 0,
            "color_tone": vmk_report.get("color_analysis", {}).get("tone", "unknown"),
            "brightness": vmk_report.get("color_analysis", {}).get("brightness_level", "unknown"),
            "contrast": vmk_report.get("color_analysis", {}).get("contrast_level", "unknown"),
            "complexity": vmk_report.get("edge_analysis", {}).get("complexity", "unknown"),
            "n_objects": len(sg.objects),
            "n_text_elements": len(text_elements),
            "n_colors": len(color_palette),
        }

        # 10. Summary (se genera desde el análisis)
        summary = self._generate_summary(vmk_report, sg, hierarchy, prompt)

        pack = SamsonVisionPack(
            version=SVP_SCHEMA_VERSION,
            metadata=metadata,
            summary=summary,
            ascii_representations=ascii_repr,
            scene_graph=sg,
            ai_description=ai_desc,
            raw_vmk=vmk_report,
        )
        return pack

    def _run_vmk(self, img) -> dict:
        """Ejecuta el Vision Multimodal Kernel."""
        from vmk import VisionMultimodalKernel
        vmk = VisionMultimodalKernel()
        result = vmk.process_image(img)
        self._vmk = vmk
        return result

    def _generate_ascii(self, img) -> dict:
        """Genera representaciones ASCII multi-estilo."""
        from samson_core import convert_image, create_visual_language
        result = {}
        # Todos los estilos
        for style in ["standard", "detail", "block", "edge", "dither", "fanart", "braille"]:
            try:
                result[style] = convert_image(img.copy(), style=style, width=80, height=30)
            except Exception as e:
                result[style] = f"[ERROR: {e}]"
        # Lenguaje visual
        try:
            result["visual_language"] = create_visual_language(img.copy(), width=50, height=30)
        except Exception as e:
            result["visual_language"] = f"[ERROR: {e}]"
        return result

    def _compute_density(self, img) -> list:
        """Mapa de densidad visual en grid 10x10."""
        gray = np.array(img.convert("L").resize((10, 10)))
        # Normalizar 0-100 (oscuro=alto=100, claro=bajo=0)
        density = ((255 - gray) / 255 * 100).round(1).tolist()
        return density

    def _extract_colors(self, img) -> list:
        """Extrae paleta de colores con nombres textuales."""
        arr = np.array(img.convert("RGB").resize((32, 32)))
        h, w = arr.shape[:2]
        total = h * w
        flat = arr.reshape(-1, 3)

        # Cuantizar a colores de 32 bits
        quantized = (flat // 64) * 64 + 32
        unique, counts = np.unique(quantized, axis=0, return_counts=True)

        # Ordenar por frecuencia
        sorted_idx = np.argsort(-counts)
        palette = []
        for i in sorted_idx[:15]:
            r, g, b = int(unique[i][0]), int(unique[i][1]), int(unique[i][2])
            pct = counts[i] / total * 100
            name = name_color(r, g, b)
            palette.append(ColorInfo(
                hex=f"#{r:02x}{g:02x}{b:02x}",
                name=name,
                percentage=round(pct, 1),
            ))
        return palette

    def _detect_text(self, img) -> list:
        """Detección de texto en imagen.
        
        Intenta pytesseract primero (OCR real con coordenadas).
        Si no está disponible, usa el método simple.
        """
        try:
            # Configurar ruta de tesseract (brew)
            import pytesseract
            import os
            
            # Rutas posibles del binario tesseract
            tesseract_paths = [
                "/home/linuxbrew/.linuxbrew/bin/tesseract",
                "/usr/bin/tesseract",
                "/usr/local/bin/tesseract",
            ]
            for tp in tesseract_paths:
                if os.path.exists(tp):
                    pytesseract.pytesseract.tesseract_cmd = tp
                    break
            
            # Configurar TESSDATA
            tessdata_paths = [
                "/home/linuxbrew/.linuxbrew/share/tessdata",
                "/usr/share/tessdata",
                "/usr/local/share/tessdata",
            ]
            for tdp in tessdata_paths:
                if os.path.exists(tdp):
                    os.environ["TESSDATA_PREFIX"] = tdp
                    break
            
            return self._detect_text_tesseract(img)
        except ImportError:
            return self._detect_text_simple(img)
        except Exception as e:
            logger.warning(f"Tesseract error: {e}")
            return self._detect_text_simple(img)

    def _detect_text_tesseract(self, img) -> list:
        """OCR con Tesseract vía pytesseract con preprocesado."""
        import pytesseract
        import numpy as np
        from PIL import Image, ImageFilter, ImageEnhance
        
        # ── Preprocesado para mejorar OCR en screenshots web ──
        # 1. Escalar 2x para texto pequeño
        w, h = img.size
        img_ocr = img.resize((w * 2, h * 2), Image.LANCZOS)
        
        # 2. Convertir a grises
        gray = img_ocr.convert("L")
        
        # 3. Aumentar contraste
        enhancer = ImageEnhance.Contrast(gray)
        gray = enhancer.enhance(1.5)
        
        # 4. Binarizar con OTSU
        arr = np.array(gray)
        # OTSU thresholding simple
        thresh = 128
        if arr.std() > 30:
            # Calcular threshold OTSU aproximado
            hist, _ = np.histogram(arr, bins=256, range=(0, 255))
            total = arr.size
            sum_total = np.dot(np.arange(256), hist)
            sum_b = 0
            w_b = 0
            w_f = 0
            var_max = 0
            threshold = 128
            for t in range(256):
                w_b += hist[t]
                if w_b == 0:
                    continue
                w_f = total - w_b
                if w_f == 0:
                    break
                sum_b += t * hist[t]
                m_b = sum_b / w_b
                m_f = (sum_total - sum_b) / w_f
                var_between = w_b * w_f * (m_b - m_f) ** 2
                if var_between > var_max:
                    var_max = var_between
                    threshold = t
            thresh = threshold
        
        binary = np.where(arr > thresh, 255, 0).astype(np.uint8)
        img_ocr_final = Image.fromarray(binary)
        
        # 5. OCR sobre la imagen preprocesada
        w_orig, h_orig = img.size  # coordenadas originales
        data = pytesseract.image_to_data(
            img_ocr_final, lang='spa+eng',
            output_type=pytesseract.Output.DICT,
            config='--psm 6 --oem 3'
        )
        
        elements = []
        n_boxes = len(data['text'])
        # Agrupar palabras en líneas (misma línea ≈ misma coordenada y)
        lines = {}
        for i in range(n_boxes):
            text = data['text'][i].strip()
            if not text:
                continue
            conf = int(data['conf'][i]) / 100.0
            if conf < 0.4:
                continue
            x, y, bw, bh = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
            if bw < 8 or bh < 8:
                continue
            # Normalizar coordenadas a la imagen original (dividir por 2)
            line_key = round(y / 20)  # agrupar por línea (~20px tolerancia)
            if line_key not in lines:
                lines[line_key] = []
            lines[line_key].append({
                'text': text, 'conf': conf,
                'x': x // 2, 'y': y // 2,
                'w': bw // 2, 'h': bh // 2,
            })
        
        # Convertir líneas a elementos
        for line_key in sorted(lines.keys()):
            words = lines[line_key]
            if not words:
                continue
            # Juntar palabras de la misma línea
            words.sort(key=lambda w: w['x'])
            full_text = " ".join(w['text'] for w in words)
            avg_conf = sum(w['conf'] for w in words) / len(words)
            x0 = min(w['x'] for w in words)
            y0 = min(w['y'] for w in words)
            x1 = max(w['x'] + w['w'] for w in words)
            y1 = max(w['y'] + w['h'] for w in words)
            
            elements.append(DetectedText(
                text=full_text,
                bbox=BBox.from_pixels(x0, y0, x1, y1, w_orig, h_orig),
                confidence=round(avg_conf, 3),
                language="spa+eng",
            ))
        
        return elements

    def _detect_text_paddle(self, img) -> list:
        """OCR con PaddleOCR."""
        from paddleocr import PaddleOCR
        ocr = PaddleOCR(lang='es', use_angle_cls=True, show_log=False)
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            img.save(f, format='PNG')
            tmp = f.name
        result = ocr.ocr(tmp)
        import os
        os.unlink(tmp)
        elements = []
        w, h = img.size
        if result and result[0]:
            for line in result[0]:
                points = line[0]  # [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
                xs = [p[0] for p in points]
                ys = [p[1] for p in points]
                bbox = BBox.from_pixels(min(xs), min(ys), max(xs), max(ys), w, h)
                elements.append(DetectedText(
                    text=line[1][0],
                    bbox=bbox,
                    confidence=round(line[1][1], 3),
                    language="es",
                ))
        return elements

    def _detect_text_simple(self, img) -> list:
        """Detección simple de zonas de texto basada en contraste local."""
        gray = np.array(img.convert("L"))
        h, w = gray.shape
        elements = []

        # Dividir en grid 10x10
        cell_w = w // 10
        cell_h = h // 10
        for gy in range(10):
            for gx in range(10):
                y0, y1 = gy * cell_h, min((gy + 1) * cell_h, h)
                x0, x1 = gx * cell_w, min((gx + 1) * cell_w, w)
                cell = gray[y0:y1, x0:x1]
                if cell.size == 0:
                    continue
                # Alto contraste local = posible texto
                local_std = cell.std()
                if local_std > 50:
                    # Probable zona de texto
                    elements.append(DetectedText(
                        text=f"[text_region_g{gy}_{gx}]",
                        bbox=BBox.from_pixels(x0, y0, x1, y1, w, h),
                        confidence=round(min(local_std / 80, 0.95), 3),
                    ))

        # Fusionar adyacentes
        merged = []
        used = set()
        for i, e1 in enumerate(elements):
            if i in used:
                continue
            group = [e1]
            used.add(i)
            for j, e2 in enumerate(elements):
                if j in used:
                    continue
                # Si están cerca horizontalmente
                if (abs(e1.bbox.y1 - e2.bbox.y1) < 15 and
                    abs(e1.bbox.x2 - e2.bbox.x1) < 10):
                    group.append(e2)
                    used.add(j)
            if group:
                xs = [g.bbox.x1 for g in group] + [g.bbox.x2 for g in group]
                ys = [g.bbox.y1 for g in group] + [g.bbox.y2 for g in group]
                merged.append(DetectedText(
                    text=f"[text_zone]",
                    bbox=BBox(min(xs), min(ys), max(xs), max(ys)),
                    confidence=round(max(g.confidence for g in group), 3),
                ))
        return merged if merged else elements

    def _build_scene_graph(self, vmk_report: dict, text_elements: list,
                           color_palette: list, density_map: list,
                           img_w: int, img_h: int) -> SceneGraphSimplified:
        """Construye el scene graph simplificado."""
        objects = []
        hierarchy = {}

        # Objetos del VMK
        sg_data = vmk_report.get("scene_graph", {})
        for node in sg_data.get("nodes", []):
            b = node.get("bbox", {})
            obj = DetectedObject(
                label=node.get("label", "unknown"),
                bbox=BBox(
                    round(b.get("x0", 0) * 100, 1),
                    round(b.get("y0", 0) * 100, 1),
                    round(b.get("x1", 1) * 100, 1),
                    round(b.get("y1", 1) * 100, 1),
                ),
                confidence=node.get("confidence", 0),
                hierarchy_level=3,
                attributes=node.get("attributes", {}),
            )
            # Asignar jerarquía por área
            if obj.bbox.area_pct > 15:
                obj.hierarchy_level = 1
            elif obj.bbox.area_pct > 5:
                obj.hierarchy_level = 2
            objects.append(obj)

            lvl = obj.hierarchy_level
            if lvl not in hierarchy:
                hierarchy[lvl] = []
            hierarchy[lvl].append(obj.label)

        # Añadir textos detectados al hierarchy
        if text_elements:
            if 3 not in hierarchy:
                hierarchy[3] = []
            hierarchy[3].append(f"text({len(text_elements)} elementos)")

        return SceneGraphSimplified(
            objects=objects,
            text_elements=text_elements,
            color_palette=color_palette,
            density_map=density_map,
            hierarchy=hierarchy,
            image_dimensions=f"{img_w}x{img_h}",
            aspect_ratio=round(img_w / img_h, 3) if img_h > 0 else 0,
        )

    def _compute_hierarchy(self, objects: list) -> dict:
        """Agrupa objetos por nivel jerárquico."""
        h = {}
        for obj in objects:
            lvl = obj.hierarchy_level
            if lvl not in h:
                h[lvl] = []
            h[lvl].append(obj.label)
        return h

    def _generate_summary(self, vmk_report: dict, sg: SceneGraphSimplified,
                           hierarchy: dict, prompt: str) -> dict:
        """Genera el resumen visual."""
        s = vmk_report.get("summary", {})

        # Descripción global
        lines = []
        if s.get("n_objects_detected", 0) > 0:
            lines.append(f"La imagen contiene {s['n_objects_detected']} regiones visuales detectadas.")
        if s.get("color_tone"):
            lines.append(f"Tonalidad general: {s['color_tone']}.")
        if s.get("complexity"):
            lines.append(f"La imagen tiene complejidad visual {s['complexity']}.")
        if sg.text_elements:
            lines.append(f"Se detectaron {len(sg.text_elements)} zonas de texto.")

        # Jerarquía
        levels_desc = {1: "PRINCIPAL", 2: "SECUNDARIO", 3: "DETALLE"}
        for lvl in sorted(hierarchy.keys()):
            if lvl in levels_desc:
                labels = hierarchy[lvl]
                lines.append(f"Nivel {lvl} ({levels_desc[lvl]}): {len(labels)} elementos.")

        return {
            "global": " ".join(lines),
            "prompt": prompt,
        }

    def _build_ai_description(self, vmk_report: dict, ascii_repr: dict,
                               sg: SceneGraphSimplified, hierarchy: dict,
                               prompt: str) -> AIDescription:
        """Construye la versión optimizada para IA sin visión."""
        s = vmk_report.get("summary", {})
        color_analysis = vmk_report.get("color_analysis", {})
        edge_analysis = vmk_report.get("edge_analysis", {})

        # Instrucciones de interpretación
        instructions = (
            "INSTRUCCIÓN PARA IA SIN VISIÓN:\n\n"
            "A continuación recibes una representación textual multi-capa de una imagen.\n"
            "NO es texto normal — es la CODIFICACIÓN VISUAL de una imagen real.\n\n"
            "Debes RECONSTRUIR MENTALMENTE la escena a partir de:\n"
            "1. Las representaciones ASCII (cada carácter codifica densidad visual)\n"
            "2. Las coordenadas normalizadas (x=0-100%, y=0-100% desde arriba-izquierda)\n"
            "3. Los objetos detectados y su jerarquía\n"
            "4. El texto OCR detectado y su posición\n"
            "5. La paleta de colores dominantes\n"
            "6. El mapa de densidad visual\n\n"
            "Interpreta los caracteres ASCII como una cuadrícula donde:\n"
            " - '#' '@' '%' = zonas oscuras / densas (elementos visuales importantes)\n"
            " - '.' ' ' = zonas claras / vacías (fondo, espacio negativo)\n"
            " - Caracteres intermedios = gradientes de densidad\n\n"
            "Usa TODAS las capas para formar una imagen mental completa."
        )

        # Layout espacial
        spatial = []
        if sg.objects:
            # Top-N por área
            sorted_objs = sorted(sg.objects, key=lambda o: -o.bbox.area_pct)
            if sorted_objs:
                spatial.append("Distribución espacial de elementos por tamaño:")
                for obj in sorted_objs[:8]:
                    b = obj.bbox
                    spatial.append(
                        f"  • {obj.label} ocupa {b.area_pct:.1f}% de la imagen "
                        f"(x:{b.x1:.0f}-{b.x2:.0f}%, y:{b.y1:.0f}-{b.y2:.0f}%)"
                    )

        if sg.text_elements:
            spatial.append("\nTexto detectado con coordenadas:")
            for t in sg.text_elements[:10]:
                b = t.bbox
                spatial.append(f"  • '{t.text[:50]}' en ({b.x1:.0f},{b.y1:.0f}) conf:{t.confidence:.2f}")

        if sg.density_map:
            spatial.append("\nMapa de densidad (grid 10x10, 0=vacío 100=denso):")
            for y, row in enumerate(sg.density_map[:6]):
                chars = "".join(" ░▒▓█"[min(int(v / 25), 4)] for v in row[:10])
                spatial.append(f"  y={y*10:2d}% {chars}")

        # Elementos importantes
        important = []
        if 1 in hierarchy:
            important.append(f"Zona principal: {', '.join(set(hierarchy[1]))}")
        if 2 in hierarchy:
            important.append(f"Zonas secundarias: {', '.join(set(hierarchy[2][:5]))}")
        if sg.text_elements:
            texts = [t.text[:30] for t in sg.text_elements[:5]]
            important.append(f"Contiene texto: {' | '.join(texts)}")
        if s.get("color_tone"):
            important.append(f"Tonalidad: {s['color_tone']}")

        colors_present = [c.name for c in sg.color_palette[:6]]

        # HTML visual simplificado
        html = self._generate_visual_html(sg)

        # Summary
        summary_parts = []
        if s.get("dimensions"):
            summary_parts.append(f"Imagen de {s['dimensions']} píxeles.")
        if s.get("color_tone"):
            summary_parts.append(f"Tono {s['color_tone']}.")
        if sg.text_elements:
            summary_parts.append(f"Contiene texto legible.")
        if s.get("n_objects_detected"):
            summary_parts.append(f"Complejidad {s['complexity']} con {s['n_objects_detected']} elementos detectados.")

        return AIDescription(
            summary=" ".join(summary_parts),
            spatial_layout="\n".join(spatial),
            important_elements=important,
            colors_present=colors_present,
            html_visual=html,
            interpretation_instructions=instructions,
        )

    def _generate_visual_html(self, sg: SceneGraphSimplified) -> str:
        """Genera HTML visual simplificado (layout + semántica)."""
        lines = ['<body visual="bridge_pack">']

        # Agrupar objetos por posición vertical
        top_objs = [o for o in sg.objects if o.bbox.y1 < 15]
        mid_objs = [o for o in sg.objects if 15 <= o.bbox.y1 < 75]
        bot_objs = [o for o in sg.objects if o.bbox.y1 >= 75]

        if top_objs:
            lines.append('  <zone name="top" density="{}">'.format(
                "high" if any(o.hierarchy_level <= 2 for o in top_objs) else "low"
            ))
            for o in top_objs[:5]:
                align = "right" if o.bbox.x1 > 50 else "left"
                lines.append(f'    <element label="{o.label}" align="{align}" '
                             f'size="{o.bbox.area_pct:.0f}%" />')
            lines.append('  </zone>')

        if mid_objs:
            lines.append('  <zone name="center" align="center">')
            center = [o for o in mid_objs if abs(o.bbox.center[0] - 50) < 25]
            for o in center[:5]:
                role = "primary" if o.hierarchy_level == 1 else "secondary"
                lines.append(f'    <element label="{o.label}" role="{role}" '
                             f'size="{o.bbox.area_pct:.0f}%" />')
            lines.append('  </zone>')

        if bot_objs:
            lines.append('  <zone name="bottom" density="low">')
            for o in bot_objs[:5]:
                lines.append(f'    <element label="{o.label}" '
                             f'size="{o.bbox.area_pct:.0f}%" />')
            lines.append('  </zone>')

        if sg.text_elements:
            lines.append('  <ocr>')
            for t in sg.text_elements[:5]:
                lines.append(f'    <text pos="({t.bbox.x1:.0f},{t.bbox.y1:.0f})" '
                             f'conf="{t.confidence:.2f}">{t.text[:40]}</text>')
            lines.append('  </ocr>')

        lines.append('</body>')
        return "\n".join(lines)

    def _error_pack(self, msg: str) -> SamsonVisionPack:
        """Crea un pack de error."""
        return SamsonVisionPack(
            version=SVP_SCHEMA_VERSION,
            metadata={"error": msg},
            summary={"global": f"[ERROR] {msg}"},
        )

    def _load_image(self, image_input):
        """Carga una imagen desde varios formatos."""
        try:
            if isinstance(image_input, Image.Image):
                return image_input
            if isinstance(image_input, str):
                if image_input.startswith("data:image"):
                    b64_data = image_input.split(",", 1)[1]
                    return Image.open(io.BytesIO(base64.b64decode(b64_data)))
                elif image_input.startswith("http"):
                    from urllib.request import urlopen
                    with urlopen(image_input, timeout=15) as resp:
                        return Image.open(io.BytesIO(resp.read()))
                else:
                    return Image.open(image_input)
            if isinstance(image_input, bytes):
                return Image.open(io.BytesIO(image_input))
        except Exception as e:
            logger.error(f"Error cargando imagen: {e}")
            return None
        return None




def generate_svp(image_path, fmt="md", prompt=""):
    """Public API: generate SVP from an image path.

    Args:
        image_path: Path to image file
        fmt: Output format — "md" (markdown) or "json"
        prompt: Optional context prompt for the builder

    Returns:
        SVP as markdown or JSON string
    """
    builder = SamsonVisionBuilder()
    pack = builder.build(image_path, prompt)
    return pack.to_markdown() if fmt == "md" else pack.to_json()


# ═══════════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════════

def cli():
    """Interfaz CLI."""
    import sys

    # Marca espiritual — Sansón no vio con sus ojos, su visión era el plan de Dios
    try:
        from versiculos import imprimir
        imprimir()
    except ImportError:
        pass

    if len(sys.argv) < 2 or sys.argv[1] in ("--help", "-h"):
        print("🦁 Samson Vision Pack CLI")
        print("Uso: samson-vision <imagen> [--json|--md] [--prompt <texto>]")
        print("")
        print("Ejemplos:")
        print("  samson-vision imagen.png --md        # SVP en Markdown")
        print("  samson-vision imagen.png --json      # SVP en JSON")
        print("  samson-vision imagen.png --md 2>/dev/null  # Sin versículo")
        print("  samson-vision imagen.png --md > svp.md     # Guardar a archivo")
        return

    path = sys.argv[1]
    fmt = "--md" if "--md" in sys.argv else "--json"
    prompt = ""
    if "--prompt" in sys.argv:
        idx = sys.argv.index("--prompt")
        if idx + 1 < len(sys.argv):
            prompt = sys.argv[idx + 1]

    builder = SamsonVisionBuilder()
    pack = builder.build(path, prompt)

    if fmt == "--json":
        print(pack.to_json())
    else:
        print(pack.to_markdown())


if __name__ == "__main__":
    cli()
