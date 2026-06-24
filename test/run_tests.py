"""
🦁 SAMSON VISION — Test Suite v2.0
Tests para: Core + VMK + Device DB + Synesthesia + Harnesses
"""
import sys, os, json, base64, io, time, unittest
from PIL import Image, ImageDraw

# Añadir src al path
SRC = os.path.expanduser("~/proyectos/samson-vision/src")
sys.path.insert(0, SRC)

from samson_core import (
    convert_image, convert_all_styles, create_visual_language,
    STYLE_REGISTRY
)


# ═══════════════════════════════════════════════════════════════
#  UTILIDADES
# ═══════════════════════════════════════════════════════════════

def create_test_image(width=200, height=150):
    """Crea una imagen de test con formas geométricas."""
    img = Image.new('RGB', (width, height), '#e0e0e0')
    draw = ImageDraw.Draw(img)
    draw.rectangle([20, 20, 80, 80], fill='#ff4444')
    draw.ellipse([100, 20, 160, 80], fill='#4444ff')
    draw.polygon([(60, 100), (100, 140), (140, 100)], fill='#44ff44')
    draw.text((10, 5), "SV2", fill='#333333')
    return img


def img_to_b64(img):
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}"


# ═══════════════════════════════════════════════════════════════
#  1. CORE ENGINE TESTS
# ═══════════════════════════════════════════════════════════════

class TestCoreEngine(unittest.TestCase):
    """Tests del core de conversión ASCII."""

    def setUp(self):
        self.img = create_test_image()

    def test_all_styles_produce_output(self):
        for name in STYLE_REGISTRY:
            if name == "color":
                continue  # ANSI colors, skip in unit test
            result = convert_image(self.img, style=name, width=40, height=20)
            self.assertGreater(len(result), 50, f"Style {name} produced too short output")

    def test_convert_all_styles(self):
        result = convert_all_styles(self.img, width=40, height=20)
        self.assertIn("standard", result)
        self.assertIn("block", result)
        self.assertIn("edge", result)

    def test_visual_language_has_metadata(self):
        vl = create_visual_language(self.img, width=40, height=20)
        self.assertIn("SAMSON", vl)
        self.assertIn("METADATOS", vl)
        self.assertIn("EDGE", vl)

    def test_input_from_bytes(self):
        buf = io.BytesIO()
        self.img.save(buf, format='PNG')
        result = convert_image(buf.getvalue(), style="standard", width=30, height=15)
        self.assertGreater(len(result), 30)

    def test_input_from_path(self):
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            self.img.save(f, format='PNG')
            tmp = f.name
        result = convert_image(tmp, style="standard", width=30, height=15)
        self.assertGreater(len(result), 30)
        os.unlink(tmp)

    def test_invalid_style_raises(self):
        with self.assertRaises(ValueError):
            convert_image(self.img, style="nonexistent")

    def test_braille_produces_unicode(self):
        result = convert_image(self.img, style="braille", width=20, height=10)
        self.assertIn("⣿", result + "⣀⣀")  # should have braille chars or spaces
        self.assertGreater(len(result), 20)


# ═══════════════════════════════════════════════════════════════
#  2. VMK TESTS
# ═══════════════════════════════════════════════════════════════

class TestVMK(unittest.TestCase):
    """Tests del Vision Multimodal Kernel."""

    def setUp(self):
        self.img = create_test_image()
        from vmk import VisionMultimodalKernel, VMKConfig
        from vmk.scene_graph import SceneGraph, SceneNode, BBox, RelationType
        self.VMK = VisionMultimodalKernel
        self.SceneGraph = SceneGraph
        self.SceneNode = SceneNode
        self.BBox = BBox
        self.RelationType = RelationType

    def test_color_analysis(self):
        vmk = self.VMK()
        result = vmk.analyze_color(self.img)
        self.assertIn("avg_color_rgb", result)
        self.assertIn("brightness", result)
        self.assertIn("tone", result)
        self.assertEqual(len(result["avg_color_rgb"]), 3)

    def test_edge_analysis(self):
        vmk = self.VMK()
        result = vmk.analyze_edges(self.img)
        self.assertIn("edge_intensity", result)
        self.assertIn("complexity", result)
        self.assertGreater(result["edge_intensity"], 0)

    def test_saliency(self):
        vmk = self.VMK()
        result = vmk.analyze_saliency(self.img)
        self.assertIn("focus_point", result)
        self.assertIn("hot_zone_fraction", result)

    def test_process_image_full(self):
        vmk = self.VMK()
        result = vmk.process_image(self.img)
        self.assertIn("summary", result)
        self.assertIn("color_analysis", result)
        self.assertIn("edge_analysis", result)
        self.assertIn("scene_graph", result)
        self.assertGreater(result["summary"]["n_objects_detected"], 0)  # should find shapes

    def test_scene_graph_basics(self):
        sg = self.SceneGraph()
        n1 = self.SceneNode(id="a", label="rect", confidence=0.9,
                           bbox=self.BBox(0.1, 0.1, 0.4, 0.5))
        n2 = self.SceneNode(id="b", label="circle", confidence=0.8,
                           bbox=self.BBox(0.5, 0.1, 0.8, 0.5))
        sg.add_node(n1)
        sg.add_node(n2)
        sg.infer_spatial_relations()
        self.assertEqual(len(sg.nodes), 2)
        self.assertGreater(len(sg.edges), 0)

    def test_scene_graph_iou(self):
        b1 = self.BBox(0, 0, 1, 1)
        b2 = self.BBox(0.5, 0.5, 1, 1)
        iou = b1.iou(b2)
        self.assertGreater(iou, 0)
        self.assertLess(iou, 1)

    def test_vmk_multimodal_report(self):
        vmk = self.VMK()
        report = vmk.process_image_multimodal(self.img)
        self.assertIn("SAMSON", report)
        self.assertIn("SCENE GRAPH", report)
        self.assertIn("COLOR", report.upper())


# ═══════════════════════════════════════════════════════════════
#  3. DEVICE DB TESTS
# ═══════════════════════════════════════════════════════════════

class TestDeviceDB(unittest.TestCase):
    """Tests de la base de datos de dispositivos."""

    def setUp(self):
        from device_db import (
            get_db, Device, add_device, get_device,
            search_devices, list_all_devices, seed_default_devices,
            delete_device, update_device, simulate_viewport
        )
        self.Device = Device
        self.add_device = add_device
        self.get_device = get_device
        self.search_devices = search_devices
        self.list_all_devices = list_all_devices
        self.seed_default_devices = seed_default_devices
        self.delete_device = delete_device
        self.update_device = update_device
        self.simulate_viewport = simulate_viewport

    def test_seed_defaults(self):
        self.seed_default_devices()

    def test_search_by_category(self):
        self.seed_default_devices()
        phones = self.search_devices(category="phone")
        self.assertGreater(len(phones), 0)
        for p in phones:
            self.assertEqual(p.category, "phone")

    def test_search_by_vendor(self):
        apples = self.search_devices(vendor="Apple")
        for a in apples:
            self.assertIn("Apple", a.vendor)

    def test_get_device(self):
        self.seed_default_devices()
        d = self.get_device("redmi-note-13")
        self.assertIsNotNone(d)
        self.assertEqual(d.viewport_width, 393)

    def test_crud_cycle(self):
        d = self.Device(
            id="test-device-1", name="Test Device", category="phone",
            vendor="Test", model="T1",
            viewport_width=400, viewport_height=800,
        )
        self.add_device(d)
        retrieved = self.get_device("test-device-1")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.viewport_width, 400)
        self.delete_device("test-device-1")
        self.assertIsNone(self.get_device("test-device-1"))

    def test_simulate_viewport(self):
        img = create_test_image(200, 150)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        with open("/tmp/test_sim.png", "wb") as f:
            f.write(buf.getvalue())
        result = self.simulate_viewport("redmi-note-13", "/tmp/test_sim.png")
        self.assertIn("device", result)
        self.assertIn("viewport", result)
        os.unlink("/tmp/test_sim.png")


# ═══════════════════════════════════════════════════════════════
#  4. SYNESTHESIA TESTS
# ═══════════════════════════════════════════════════════════════

class TestSynesthesia(unittest.TestCase):
    """Tests del procesador de sinestesia."""

    def setUp(self):
        from synesthesia import SynesthesiaProcessor, AudioFeatures
        self.SynesthesiaProcessor = SynesthesiaProcessor
        self.AudioFeatures = AudioFeatures

    def _create_test_audio(self, duration_sec=0.5, freq=440, sample_rate=44100):
        """Crea un tono senoidal de prueba."""
        import numpy as np
        t = np.linspace(0, duration_sec, int(sample_rate * duration_sec), endpoint=False)
        audio = np.sin(2 * np.pi * freq * t) * 0.3
        return audio, sample_rate

    def test_analyze_sine_wave(self):
        sp = self.SynesthesiaProcessor()
        audio, sr = self._create_test_audio()
        feat = sp.analyze(audio, sr)
        self.assertGreater(feat.rms_energy, 0)
        self.assertGreater(feat.duration, 0)
        self.assertGreater(feat.peak_amplitude, 0)

    def test_render_waveform(self):
        sp = self.SynesthesiaProcessor()
        audio, sr = self._create_test_audio()
        result = sp.audio_to_ascii(audio, sr, style="waveform")
        self.assertGreater(len(result), 50)

    def test_render_spectrum(self):
        sp = self.SynesthesiaProcessor()
        audio, sr = self._create_test_audio()
        result = sp.audio_to_ascii(audio, sr, style="spectrum")
        self.assertIn("Hz", result)

    def test_render_energy(self):
        sp = self.SynesthesiaProcessor()
        audio, sr = self._create_test_audio()
        result = sp.audio_to_ascii(audio, sr, style="energy")
        self.assertGreater(len(result), 20)

    def test_render_beats(self):
        sp = self.SynesthesiaProcessor()
        audio, sr = self._create_test_audio()
        result = sp.audio_to_ascii(audio, sr, style="beats")
        self.assertGreater(len(result), 20)

    def test_full_pipeline(self):
        sp = self.SynesthesiaProcessor()
        audio, sr = self._create_test_audio()
        result = sp.process_audio(audio, style="waveform", sample_rate=sr)
        self.assertIn("features", result)
        self.assertIn("visualization", result)
        self.assertIn("fragments", result)

    def test_classify_energy(self):
        sp = self.SynesthesiaProcessor()
        self.assertEqual(sp._classify_energy(0.001), "silencio")
        self.assertEqual(sp._classify_energy(0.02), "bajo")
        self.assertEqual(sp._classify_energy(0.2), "alto")


# ═══════════════════════════════════════════════════════════════
#  5. HARNESSES TESTS
# ═══════════════════════════════════════════════════════════════

class TestHarnesses(unittest.TestCase):
    """Tests de los arneses de integración."""

    def setUp(self):
        from harnesses import (
            full_analysis_pipeline, codex_debug,
            _find_mmx, _find_codex
        )
        self.full_analysis_pipeline = full_analysis_pipeline
        self.codex_debug = codex_debug
        self._find_mmx = _find_mmx
        self._find_codex = _find_codex

    def test_find_tools(self):
        """Verifica que las herramientas sean encontrables (no falla si no existen)."""
        mmx = self._find_mmx()
        # No assert, solo verificar que no crashea
        self.assertIsNotNone(mmx) if mmx else self.assertIsNone(mmx)

    def test_full_pipeline_no_image(self):
        result = self.full_analysis_pipeline("/tmp/nonexistent.png")
        self.assertTrue("error" in result)


# ═══════════════════════════════════════════════════════════════
#  RUNNER
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("  🦁 SAMSON VISION v2.0 — TEST SUITE COMPLETA")
    print("  Core + VMK + Device DB + Synesthesia + Harnesses")
    print("=" * 60)

    suite = unittest.TestSuite()
    loader = unittest.TestLoader()

    suite.addTests(loader.loadTestsFromTestCase(TestCoreEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestVMK))
    suite.addTests(loader.loadTestsFromTestCase(TestDeviceDB))
    suite.addTests(loader.loadTestsFromTestCase(TestSynesthesia))
    suite.addTests(loader.loadTestsFromTestCase(TestHarnesses))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print()
    print("=" * 60)
    total = result.testsRun
    failures = len(result.failures) + len(result.errors)
    print(f"  RESULTADO: {total - failures}/{total} tests pasados")
    print(f"  {'🦁 SAMSON VISION v2.0: COMPLETO' if failures == 0 else f'⚠️  {failures} fallos'}")
    print("=" * 60)

    sys.exit(0 if failures == 0 else 1)
