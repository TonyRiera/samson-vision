"""
🦁 VMK Kernel — Orquestador multimodal de análisis visual.

El VMK es el cerebro de Samson Vision:
1. Recibe una imagen
2. Aplica análisis multi-capa (color, bordes, texturas, objetos)
3. Construye un Scene Graph con objetos y relaciones espaciales
4. Genera representaciones ASCII de cada capa
5. Produce un informe visual estructurado para el LLM
"""
import io
import base64
import logging
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path

from PIL import Image
import numpy as np

from .scene_graph import SceneGraph, SceneNode, BBox, RelationType

logger = logging.getLogger("vmk")


@dataclass
class VMKConfig:
    """Configuración del VMK."""
    max_width: int = 80
    max_height: int = 60
    min_object_area: int = 200  # píxeles mínimos para considerar un objeto
    enable_scene_graph: bool = True
    enable_color_analysis: bool = True
    enable_edge_analysis: bool = True
    enable_saliency: bool = True  # mapa de prominencia visual


class VisionMultimodalKernel:
    """
    Kernel multimodal de visión.

    Orquesta análisis multi-capa y produce un informe estructurado
    que cualquier LLM puede entender.
    """

    def __init__(self, config: Optional[VMKConfig] = None):
        self.config = config or VMKConfig()
        self._last_scene_graph: Optional[SceneGraph] = None

    # ─── Análisis por capas ────────────────────────────────────

    def analyze_color(self, img: Image.Image) -> dict:
        """Capa 1: Análisis de color."""
        rgb = img.convert("RGB")
        arr = np.array(rgb)
        h, w = arr.shape[:2]

        # Color promedio
        avg_color = tuple(int(x) for x in arr.mean(axis=(0, 1)))

        # Brillo y contraste
        gray = np.array(img.convert("L"))
        brightness = int(gray.mean())
        contrast = int(gray.std())

        # Paleta de colores dominantes (cuantización)
        flat = arr.reshape(-1, 3)
        sampled = flat[::max(1, len(flat) // 1000)]
        quantized = (sampled // 64) * 64 + 32
        unique = {tuple(int(c) for c in row) for row in quantized}
        sorted_colors = sorted(
            unique,
            key=lambda c: -np.sum((np.array(c) - np.array(avg_color)) ** 2),
        )

        # Clasificar tonalidad general
        r, g, b = avg_color
        if r > g + 30 and r > b + 30:
            tone = "rojizo/cálido"
        elif g > r + 30 and g > b + 30:
            tone = "verdoso"
        elif b > r + 30 and b > g + 30:
            tone = "azulado/frío"
        elif abs(r - g) < 20 and abs(g - b) < 20 and r > 150:
            tone = "claro/neutro"
        elif abs(r - g) < 20 and abs(g - b) < 20 and r < 100:
            tone = "oscuro/neutro"
        else:
            tone = "mixto"

        return {
            "avg_color_rgb": avg_color,
            "brightness": brightness,
            "contrast": contrast,
            "tone": tone,
            "n_unique_colors": len(unique),
            "top_colors": [tuple(c) for c in sorted_colors[:8]],
            "brightness_level": "alto" if brightness > 170 else "medio" if brightness > 85 else "bajo",
            "contrast_level": "alto" if contrast > 60 else "medio" if contrast > 30 else "bajo",
        }

    def analyze_edges(self, img: Image.Image) -> dict:
        """Capa 2: Análisis de bordes y contornos."""
        gray = np.array(img.convert("L")).astype(float)
        h, w = gray.shape

        # Sobel horizontal y vertical
        gx = np.abs(np.diff(gray, axis=1, append=gray[:, -1:]))
        gy = np.abs(np.diff(gray, axis=0, append=gray[-1:, :]))
        edges = np.sqrt(gx**2 + gy**2)

        # Estadísticas de bordes
        edge_intensity = float(edges.mean())
        edge_density = float((edges > 30).mean())  # fracción de píxeles con borde

        # Dirección dominante
        gx_mean = float(np.mean(np.abs(gx)))
        gy_mean = float(np.mean(np.abs(gy)))
        if gx_mean > gy_mean * 2:
            dominant_direction = "horizontal"
        elif gy_mean > gx_mean * 2:
            dominant_direction = "vertical"
        else:
            dominant_direction = "mixto/diagonal"

        return {
            "edge_intensity": edge_intensity,
            "edge_density": edge_density,
            "dominant_direction": dominant_direction,
            "n_contours": int(edge_density * 100),  # estimación
            "complexity": "alta" if edge_density > 0.15 else "media" if edge_density > 0.05 else "baja",
        }

    def detect_objects_simple(self, img: Image.Image) -> list:
        """
        Capa 3: Detección de objetos. Usa OpenCV si está disponible,
        con fallback a numpy+PIL.
        """
        try:
            return self._detect_objects_cv2(img)
        except ImportError:
            return self._detect_objects_numpy(img)
        except Exception as e:
            logger.warning(f"OpenCV detection failed: {e}, falling back")
            return self._detect_objects_numpy(img)

    def _detect_objects_cv2(self, img: Image.Image) -> list:
        """Detección de objetos con OpenCV (contornos + bounding boxes)."""
        import cv2
        arr = np.array(img.convert("RGB"))
        opencv_img = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(opencv_img, cv2.COLOR_BGR2GRAY)
        
        # Preprocesar
        blurred = cv2.GaussianBlur(gray, (5, 5), 1.4)
        edges = cv2.Canny(blurred, 30, 100)
        
        # Dilatar para cerrar contornos
        kernel = np.ones((3,3), np.uint8)
        dilated = cv2.dilate(edges, kernel, iterations=1)
        
        # Encontrar contornos
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        h, w = gray.shape
        detections = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 500:  # filtrar ruido
                continue
            x, y, cw, ch = cv2.boundingRect(cnt)
            detections.append({
                "bbox_normalized": (x/w, y/h, (x+cw)/w, (y+ch)/h),
                "bbox_pixels": (x, y, x+cw, y+ch),
                "area_normalized": cw*ch/(w*h),
                "area_pixels": cw*ch,
            })
        
        # Ordenar por área descendente
        detections.sort(key=lambda d: -d["area_pixels"])
        return detections[:20]  # max 20 objetos

    def _detect_objects_numpy(self, img: Image.Image) -> list:
        arr = np.array(img.convert("RGB"))
        h, w = arr.shape[:2]
        
        # Cuantizar colores a 32 niveles para reducir ruido
        quantized = (arr // 32) * 32
        
        # Dividir en superpíxeles de grid_size
        grid_size = max(16, min(w, h) // 15)
        
        regions = []
        for gy in range(0, h, grid_size):
            for gx in range(0, w, grid_size):
                y0, y1 = gy, min(gy + grid_size, h)
                x0, x1 = gx, min(gx + grid_size, w)
                cell = quantized[y0:y1, x0:x1]
                if cell.size == 0:
                    continue
                
                # Color medio de la celda
                mean_color = cell.mean(axis=(0, 1))
                # Desviación estándar (uniformidad)
                std_color = cell.std(axis=(0, 1)).mean()
                
                # Brillo medio
                gray = np.array(img.convert("L").crop((x0, y0, x1, y1)))
                brightness = gray.mean()
                
                # Detectar si esta celda tiene contenido significativo
                # (no es blanco puro o gris muy claro)
                is_content = (
                    (mean_color < 240).any() or  # no es blanco
                    std_color > 15 or             # tiene variación
                    brightness < 230              # es oscura
                )
                
                if not is_content:
                    continue
                    
                regions.append({
                    "bbox_normalized": (x0/w, y0/h, x1/w, y1/h),
                    "bbox_pixels": (x0, y0, x1, y1),
                    "area_normalized": (x1-x0)*(y1-y0)/(w*h),
                    "area_pixels": (x1-x0)*(y1-y0),
                    "avg_color_rgb": tuple(int(c) for c in mean_color),
                    "uniformity": float(std_color),
                })

        # Fusionar regiones adyacentes con colores similares
        merged = []
        used = set()
        for i, r1 in enumerate(regions):
            if i in used:
                continue
            group = [r1]
            used.add(i)
            for j, r2 in enumerate(regions):
                if j in used:
                    continue
                if (self._regions_adjacent(r1, r2) and 
                    self._color_distance(r1["avg_color_rgb"], r2["avg_color_rgb"]) < 40):
                    group.append(r2)
                    used.add(j)
            
            if group:
                xs = [r["bbox_pixels"][0] for r in group] + [r["bbox_pixels"][2] for r in group]
                ys = [r["bbox_pixels"][1] for r in group] + [r["bbox_pixels"][3] for r in group]
                avg_c = tuple(int(np.mean([r["avg_color_rgb"][c] for r in group])) for c in range(3))
                merged.append({
                    "bbox_normalized": (min(xs)/w, min(ys)/h, max(xs)/w, max(ys)/h),
                    "bbox_pixels": (min(xs), min(ys), max(xs), max(ys)),
                    "area_normalized": (max(xs)-min(xs))*(max(ys)-min(ys))/(w*h),
                    "area_pixels": (max(xs)-min(xs))*(max(ys)-min(ys)),
                    "avg_color_rgb": avg_c,
                })

        # Si no se detectó nada o hay demasiadas regiones, 
        # usar un método más restrictivo
        if len(merged) > 30:
            # Filtrar solo las regiones más grandes (>1% del área)
            merged = [r for r in merged if r["area_normalized"] > 0.01]
        
        return merged if merged else regions[:10]  # max 10 si no hubo merge

    def _regions_adjacent(self, r1: dict, r2: dict) -> bool:
        """Comprueba si dos regiones son adyacentes."""
        b1 = r1["bbox_pixels"]
        b2 = r2["bbox_pixels"]
        # Separación en cualquier eje
        dx = max(0, max(b1[0], b2[0]) - min(b1[2], b2[2]))
        dy = max(0, max(b1[1], b2[1]) - min(b1[3], b2[3]))
        return dx < 5 and dy < 5

    def _color_distance(self, c1, c2) -> float:
        """Distancia euclidiana entre colores RGB."""
        return np.sqrt(sum((a - b) ** 2 for a, b in zip(c1, c2)))

    def analyze_saliency(self, img: Image.Image) -> dict:
        """
        Capa 4: Mapa de prominencia visual.
        Detecta qué zonas de la imagen atraen más la atención.
        """
        gray = np.array(img.convert("L")).astype(float)
        h, w = gray.shape

        # Prominencia simple: diferencia del promedio local
        # Usar filtro de media con numpy (sin scipy)
        kernel_size = max(3, min(h, w) // 10)
        # Asegurar impar
        if kernel_size % 2 == 0:
            kernel_size += 1
        pad = kernel_size // 2

        # Promedio local vía convolución simple
        padded = np.pad(gray, pad, mode='reflect')
        local_mean = np.zeros_like(gray)
        for dy in range(kernel_size):
            for dx in range(kernel_size):
                local_mean += padded[dy:dy+h, dx:dx+w]
        local_mean /= kernel_size ** 2

        saliency = np.abs(gray - local_mean)

        # Zonas de interés
        threshold = saliency.mean() + saliency.std()
        hot_zones = saliency > threshold

        # Centro de masa de la zona más prominente
        if hot_zones.any():
            hot_indices = np.where(hot_zones)
            cy = int(hot_indices[0].mean())
            cx = int(hot_indices[1].mean())
            focus_point = (cx / w, cy / h)
        else:
            focus_point = (0.5, 0.5)

        # Región más prominente
        if hot_zones.any():
            hot_region = np.where(hot_zones, saliency, 0)
            max_idx = np.unravel_index(hot_region.argmax(), hot_region.shape)
            peak = (max_idx[1] / w, max_idx[0] / h)
        else:
            peak = (0.5, 0.5)

        return {
            "focus_point": focus_point,
            "peak_point": peak,
            "saliency_mean": float(saliency.mean()),
            "saliency_max": float(saliency.max()),
            "hot_zone_fraction": float(hot_zones.mean()),
        }

    # ─── Orquestación ─────────────────────────────────────────

    def process_image(self, image_input, width: int = 80, height: int = 60) -> dict:
        """
        Procesa una imagen con todas las capas de análisis.

        Args:
            image_input: PIL Image, bytes, ruta, o base64 data URI
            width, height: Dimensiones para ASCII output

        Returns:
            Dict con análisis completo
        """
        # Cargar imagen
        img = self._load_image(image_input)
        if img is None:
            return {"error": "No se pudo cargar la imagen"}

        orig_w, orig_h = img.size

        # 1. Análisis de color
        color_info = self.analyze_color(img) if self.config.enable_color_analysis else {}

        # 2. Análisis de bordes
        edge_info = self.analyze_edges(img) if self.config.enable_edge_analysis else {}

        # 3. Detección de objetos
        detections = self.detect_objects_simple(img)
        objects = []
        for i, det in enumerate(detections):
            bn = det["bbox_normalized"]
            bbox = BBox(bn[0], bn[1], bn[2], bn[3])
            area = det["area_normalized"]

            # Clasificar por tamaño
            if area > 0.3:
                label = "large_region"
            elif area > 0.1:
                label = "medium_region"
            elif area > 0.03:
                label = "small_region"
            else:
                label = "tiny_region"

            color_rgb = det.get("avg_color_rgb", (128, 128, 128))
            node = SceneNode(
                id=f"obj_{i}",
                label=label,
                confidence=min(1.0, area * 5),
                bbox=bbox,
                attributes={
                    "area_pct": round(area * 100, 1),
                    "color_rgb": color_rgb,
                },
            )
            objects.append(node)

        # 4. Scene Graph
        scene_graph = SceneGraph(
            nodes=objects,
            image_width=orig_w,
            image_height=orig_h,
        )
        if objects:
            scene_graph.infer_spatial_relations()

        # 5. Prominencia
        saliency_info = self.analyze_saliency(img) if self.config.enable_saliency else {}

        # 6. Resumen visual
        summary = {
            "dimensions": f"{orig_w}x{orig_h}",
            "aspect_ratio": round(orig_w / orig_h, 3) if orig_h > 0 else 0,
            "n_objects_detected": len(objects),
            "color_tone": color_info.get("tone", "unknown"),
            "brightness": color_info.get("brightness_level", "unknown"),
            "contrast": color_info.get("contrast_level", "unknown"),
            "complexity": edge_info.get("complexity", "unknown"),
            "focus_point": saliency_info.get("focus_point", (0.5, 0.5)),
        }

        # 7. Informe completo
        report = {
            "summary": summary,
            "color_analysis": color_info,
            "edge_analysis": edge_info,
            "saliency": saliency_info,
            "scene_graph": scene_graph.to_dict(),
        }

        # Guardar para referencia
        self._last_scene_graph = scene_graph

        return report

    def process_image_multimodal(self, image_input, prompt: str = "",
                                  width: int = 60, height: int = 40) -> str:
        """
        Procesa imagen y genera un informe textual completo para el LLM.
        Es el método principal que usa el servidor.
        """
        import sys, os
        _src = os.path.expanduser("~/proyectos/samson-vision/src")
        if _src not in sys.path:
            sys.path.insert(0, _src)
        from samson_core import create_visual_language

        img = self._load_image(image_input)
        if img is None:
            return "[ERROR: No se pudo cargar la imagen]"

        # 1. Análisis VMK
        analysis = self.process_image(img, width=width, height=height)
        if "error" in analysis:
            return f"[ERROR: {analysis['error']}]"

        # 2. Lenguaje visual ASCII multi-capa
        visual_lang = create_visual_language(img, width=width, height=height)

        # 3. Scene graph textual
        sg_text = self._last_scene_graph.to_text() if self._last_scene_graph else ""

        # 4. Informe consolidado
        s = analysis["summary"]
        report_lines = [
            "🦁 **SAMSON VISION — ANÁLISIS MULTIMODAL**",
            "=" * 60,
            "",
            f"📐 Dimensiones: {s['dimensions']} | Aspect ratio: {s['aspect_ratio']}",
            f"🎨 Tono: {s['color_tone']} | Brillo: {s['brightness']} | Contraste: {s['contrast']}",
            f"🔍 Complejidad: {s['complexity']} | Objetos: {s['n_objects_detected']}",
            "",
            "─" * 60,
            "📊 ANÁLISIS DE COLOR",
            "─" * 60,
            f"  Color dominante: RGB{analysis.get('color_analysis', {}).get('avg_color_rgb', '?')}",
            f"  Brillo medio: {analysis.get('color_analysis', {}).get('brightness', 0)}/255",
            f"  Contraste: {analysis.get('color_analysis', {}).get('contrast', 0)}/255",
            f"  Colores únicos: ~{analysis.get('color_analysis', {}).get('n_unique_colors', 0)}",
            "",
            "─" * 60,
            "🔲 ANÁLISIS DE BORDES",
            "─" * 60,
            f"  Intensidad: {analysis.get('edge_analysis', {}).get('edge_intensity', 0):.1f}",
            f"  Densidad: {analysis.get('edge_analysis', {}).get('edge_density', 0):.1%}",
            f"  Dirección dominante: {analysis.get('edge_analysis', {}).get('dominant_direction', '?')}",
            "",
            "─" * 60,
            sg_text,
            "",
        ]

        report = "\n".join(report_lines)
        full = f"{report}\n\n{visual_lang}\n\n"
        if prompt:
            full += f"=== CONSULTA ===\n{prompt}\n\n"
        full += (
            "Basándote en las representaciones ASCII multi-capa y el análisis "
            "estructurado arriba, responde a la consulta sobre la imagen."
        )
        return full

    # ─── Utilidades ────────────────────────────────────────────

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
            if isinstance(image_input, Path):
                return Image.open(str(image_input))
        except Exception as e:
            logger.error(f"Error cargando imagen: {e}")
            return None
        return None

    def get_last_scene_graph(self) -> Optional[SceneGraph]:
        """Devuelve el último Scene Graph generado."""
        return self._last_scene_graph

    def report_as_json(self, image_input) -> dict:
        """Devuelve el análisis completo como JSON."""
        return self.process_image(image_input)
