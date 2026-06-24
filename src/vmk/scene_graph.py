"""
🦁 Scene Graph — Representación estructurada de objetos en la imagen.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional


class RelationType(str, Enum):
    LEFT = "left_of"
    RIGHT = "right_of"
    ABOVE = "above"
    BELOW = "below"
    INSIDE = "inside"
    CONTAINS = "contains"
    OVERLAPS = "overlaps"
    NEAR = "near"


@dataclass
class BBox:
    """Bounding box normalizado [0-1]."""
    x0: float  # left
    y0: float  # top
    x1: float  # right
    y1: float  # bottom

    @property
    def width(self) -> float:
        return self.x1 - self.x0

    @property
    def height(self) -> float:
        return self.y1 - self.y0

    @property
    def center_x(self) -> float:
        return (self.x0 + self.x1) / 2

    @property
    def center_y(self) -> float:
        return (self.y0 + self.y1) / 2

    @property
    def area(self) -> float:
        return self.width * self.height

    def iou(self, other: "BBox") -> float:
        """Intersection over Union."""
        xi0 = max(self.x0, other.x0)
        yi0 = max(self.y0, other.y0)
        xi1 = min(self.x1, other.x1)
        yi1 = min(self.y1, other.y1)
        inter = max(0, xi1 - xi0) * max(0, yi1 - yi0)
        union = self.area + other.area - inter
        return inter / union if union > 0 else 0.0

    def contains(self, other: "BBox") -> bool:
        """True if this bbox fully contains other."""
        return (self.x0 <= other.x0 and self.y0 <= other.y0
                and self.x1 >= other.x1 and self.y1 >= other.y1)


@dataclass
class SceneNode:
    """Un objeto detectado en la imagen."""
    id: str
    label: str  # tipo de objeto (e.g., "person", "car", "text")
    confidence: float  # 0-1
    bbox: BBox
    attributes: dict = field(default_factory=dict)
    # Atributos típicos: color_dominante, brillo, area_relativa, etc.


@dataclass
class Relation:
    """Relación espacial entre dos nodos."""
    source_id: str
    target_id: str
    relation: RelationType
    confidence: float = 1.0


@dataclass
class SceneGraph:
    """Grafo completo de la escena."""
    nodes: list = field(default_factory=list)
    edges: list = field(default_factory=list)
    image_width: int = 0
    image_height: int = 0
    metadata: dict = field(default_factory=dict)

    def add_node(self, node: SceneNode):
        self.nodes.append(node)

    def add_edge(self, source_id: str, target_id: str,
                 relation: RelationType, confidence: float = 1.0):
        self.edges.append(Relation(source_id, target_id, relation, confidence))

    def get_node(self, node_id: str) -> Optional[SceneNode]:
        for n in self.nodes:
            if n.id == node_id:
                return n
        return None

    def infer_spatial_relations(self):
        """Infere relaciones espaciales entre todos los nodos."""
        self.edges.clear()
        for i, a in enumerate(self.nodes):
            for j, b in enumerate(self.nodes):
                if i >= j:
                    continue
                # Centro relativo
                if a.bbox.iou(b.bbox) > 0.1:
                    self.add_edge(a.id, b.id, RelationType.OVERLAPS)
                elif a.bbox.contains(b.bbox):
                    self.add_edge(a.id, b.id, RelationType.CONTAINS)
                elif b.bbox.contains(a.bbox):
                    self.add_edge(b.id, a.id, RelationType.CONTAINS)
                # Relaciones direccionales
                dx = b.bbox.center_x - a.bbox.center_x
                dy = b.bbox.center_y - a.bbox.center_y
                dist = (dx**2 + dy**2) ** 0.5
                if dist < 0.3:
                    self.add_edge(a.id, b.id, RelationType.NEAR)
                if abs(dx) > abs(dy):
                    if dx > 0:
                        self.add_edge(a.id, b.id, RelationType.LEFT)
                    else:
                        self.add_edge(b.id, a.id, RelationType.LEFT)
                else:
                    if dy > 0:
                        self.add_edge(a.id, b.id, RelationType.ABOVE)
                    else:
                        self.add_edge(b.id, a.id, RelationType.ABOVE)

    def to_dict(self) -> dict:
        """Serializa a dict para JSON."""
        return {
            "nodes": [
                {
                    "id": n.id,
                    "label": n.label,
                    "confidence": n.confidence,
                    "bbox": asdict(n.bbox),
                    "attributes": n.attributes,
                }
                for n in self.nodes
            ],
            "edges": [
                {"source": e.source_id, "target": e.target_id,
                 "relation": e.relation.value, "confidence": e.confidence}
                for e in self.edges
            ],
            "image_dimensions": {
                "width": self.image_width,
                "height": self.image_height,
            },
            "metadata": self.metadata,
        }

    def to_text(self) -> str:
        """Representación textual del scene graph."""
        lines = ["🕸️ SCENE GRAPH", "=" * 50]
        # Nodos
        if self.nodes:
            lines.append(f"\n📦 Objetos ({len(self.nodes)}):")
            for n in sorted(self.nodes,
                           key=lambda x: -x.bbox.area):
                b = n.bbox
                lines.append(
                    f"  [{n.id}] {n.label} (conf:{n.confidence:.2f}) "
                    f"pos:({b.x0:.2f},{b.y0:.2f})-({b.x1:.2f},{b.y1:.2f}) "
                    f"area:{b.area:.3f}"
                )
                if n.attributes:
                    for k, v in n.attributes.items():
                        lines.append(f"    {k}: {v}")
        else:
            lines.append("\n📦 Objetos: ninguno detectado")

        # Relaciones
        if self.edges:
            lines.append(f"\n🔗 Relaciones ({len(self.edges)}):")
            for e in self.edges:
                lines.append(f"  {e.source_id} → {e.relation.value} → {e.target_id}")
        else:
            lines.append("\n🔗 Relaciones: ningunas")

        lines.append(f"\n📐 Dimensiones: {self.image_width}x{self.image_height}")
        if self.metadata:
            lines.append(f"📊 Metadatos: {self.metadata}")
        return "\n".join(lines)

    def __repr__(self):
        return f"SceneGraph({len(self.nodes)} nodes, {len(self.edges)} edges, {self.image_width}x{self.image_height})"
