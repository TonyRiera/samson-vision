"""
🦁 VMK — Vision Multimodal Kernel
Orquestador multi-capa para análisis visual:
  1. Scene Graph (objetos, posiciones, relaciones espaciales)
  2. ASCII Renderer (8 estilos delegados a samson_core)
  3. Kernel (orquestación y análisis multimodal)
"""
from .scene_graph import SceneGraph, SceneNode, Relation, BBox
from .kernel import VisionMultimodalKernel, VMKConfig

__all__ = [
    "SceneGraph", "SceneNode", "Relation", "BBox",
    "VisionMultimodalKernel", "VMKConfig",
]
