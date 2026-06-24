"""
🦁 Device DB — Base de datos de dispositivos para testing visual responsive.

Almacena información de viewport, densidad, aspect ratio, capacidades CSS/HTML5
de dispositivos reales para simular cómo se ve una imagen en distintos formatos.
"""
import sqlite3
import json
import os
from dataclasses import dataclass, field, asdict
from typing import Optional

DB_PATH = os.path.expanduser("~/.hermes/samson-vision/device_db.sqlite")


# ─── Esquema de datos ──────────────────────────────────────────

@dataclass
class Device:
    """Un dispositivo real o simulado."""
    id: str  # identificador único
    name: str  # nombre legible
    category: str  # "phone", "tablet", "desktop", "watch", "tv", "ereader"
    vendor: str = ""  # "Apple", "Samsung", "Xiaomi", etc.
    model: str = ""  # "iPhone 15", "Redmi Note 13"
    
    # Viewport (CSS pixels)
    viewport_width: int = 0
    viewport_height: int = 0
    
    # Pantalla física
    device_pixel_ratio: float = 1.0  # DPR
    screen_width_px: int = 0  # píxeles físicos
    screen_height_px: int = 0
    physical_size_inches: float = 0  # diagonal en pulgadas
    
    # Capacidades
    css_features: dict = field(default_factory=lambda: {
        "hover": True,
        "pointer": "fine",
        "any-hover": True,
        "any-pointer": "fine",
        "color-gamut": "srgb",
        "prefers-color-scheme": "light",
        "prefers-reduced-motion": "no-preference",
        "prefers-contrast": "no-preference",
    })
    html5_features: dict = field(default_factory=lambda: {
        "touch": False,
        "webgl": True,
        "webrtc": True,
        "geolocation": True,
        "service_worker": True,
        "local_storage": True,
    })
    
    # Tags para búsqueda
    tags: list = field(default_factory=list)  # ["xiaomi", "android", "redmi"]
    
    # Metadatos
    notes: str = ""


# ─── Database ──────────────────────────────────────────────────

def get_db() -> sqlite3.Connection:
    """Abre conexión a la base de datos, creándola si no existe."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    _init_schema(conn)
    return conn


def _init_schema(conn: sqlite3.Connection):
    """Crea las tablas si no existen."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS devices (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            vendor TEXT DEFAULT '',
            model TEXT DEFAULT '',
            viewport_width INTEGER DEFAULT 0,
            viewport_height INTEGER DEFAULT 0,
            device_pixel_ratio REAL DEFAULT 1.0,
            screen_width_px INTEGER DEFAULT 0,
            screen_height_px INTEGER DEFAULT 0,
            physical_size_inches REAL DEFAULT 0,
            css_features TEXT DEFAULT '{}',
            html5_features TEXT DEFAULT '{}',
            tags TEXT DEFAULT '[]',
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_devices_category ON devices(category);
        CREATE INDEX IF NOT EXISTS idx_devices_vendor ON devices(vendor);
    """)
    conn.commit()


# ─── CRUD ──────────────────────────────────────────────────────

def add_device(device: Device) -> bool:
    """Añade un dispositivo a la DB. True si se insertó, False si ya existía."""
    conn = get_db()
    try:
        conn.execute("""
            INSERT INTO devices (id, name, category, vendor, model,
                viewport_width, viewport_height, device_pixel_ratio,
                screen_width_px, screen_height_px, physical_size_inches,
                css_features, html5_features, tags, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            device.id, device.name, device.category, device.vendor, device.model,
            device.viewport_width, device.viewport_height, device.device_pixel_ratio,
            device.screen_width_px, device.screen_height_px, device.physical_size_inches,
            json.dumps(device.css_features),
            json.dumps(device.html5_features),
            json.dumps(device.tags),
            device.notes,
        ))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def get_device(device_id: str) -> Optional[Device]:
    """Obtiene un dispositivo por ID."""
    conn = get_db()
    row = conn.execute("SELECT * FROM devices WHERE id = ?", (device_id,)).fetchone()
    conn.close()
    if row is None:
        return None
    return _row_to_device(row)


def search_devices(category: str = None, vendor: str = None,
                    min_width: int = None, max_width: int = None,
                    tag: str = None) -> list:
    """Busca dispositivos con filtros opcionales."""
    conn = get_db()
    query = "SELECT * FROM devices WHERE 1=1"
    params = []
    
    if category:
        query += " AND category = ?"
        params.append(category)
    if vendor:
        query += " AND vendor LIKE ?"
        params.append(f"%{vendor}%")
    if min_width is not None:
        query += " AND viewport_width >= ?"
        params.append(min_width)
    if max_width is not None:
        query += " AND viewport_width <= ?"
        params.append(max_width)
    if tag:
        query += " AND tags LIKE ?"
        params.append(f"%{tag}%")
    
    query += " ORDER BY category, viewport_width ASC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [_row_to_device(r) for r in rows]


def list_all_devices() -> list:
    """Lista todos los dispositivos."""
    conn = get_db()
    rows = conn.execute("SELECT * FROM devices ORDER BY category, name").fetchall()
    conn.close()
    return [_row_to_device(r) for r in rows]


def update_device(device: Device) -> bool:
    """Actualiza un dispositivo existente."""
    conn = get_db()
    cursor = conn.execute("""
        UPDATE devices SET
            name=?, category=?, vendor=?, model=?,
            viewport_width=?, viewport_height=?, device_pixel_ratio=?,
            screen_width_px=?, screen_height_px=?, physical_size_inches=?,
            css_features=?, html5_features=?, tags=?, notes=?
        WHERE id=?
    """, (
        device.name, device.category, device.vendor, device.model,
        device.viewport_width, device.viewport_height, device.device_pixel_ratio,
        device.screen_width_px, device.screen_height_px, device.physical_size_inches,
        json.dumps(device.css_features),
        json.dumps(device.html5_features),
        json.dumps(device.tags),
        device.notes,
        device.id,
    ))
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return updated


def delete_device(device_id: str) -> bool:
    """Elimina un dispositivo."""
    conn = get_db()
    cursor = conn.execute("DELETE FROM devices WHERE id = ?", (device_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


def _row_to_device(row: sqlite3.Row) -> Device:
    """Convierte una fila SQLite a objeto Device."""
    return Device(
        id=row["id"],
        name=row["name"],
        category=row["category"],
        vendor=row["vendor"],
        model=row["model"],
        viewport_width=row["viewport_width"],
        viewport_height=row["viewport_height"],
        device_pixel_ratio=row["device_pixel_ratio"],
        screen_width_px=row["screen_width_px"],
        screen_height_px=row["screen_height_px"],
        physical_size_inches=row["physical_size_inches"],
        css_features=json.loads(row["css_features"]),
        html5_features=json.loads(row["html5_features"]),
        tags=json.loads(row["tags"]),
        notes=row["notes"],
    )


# ─── Dispositivos por defecto ──────────────────────────────────

DEFAULT_DEVICES = [
    # Teléfonos
    Device(id="redmi-note-13", name="Redmi Note 13", category="phone",
           vendor="Xiaomi", model="Redmi Note 13",
           viewport_width=393, viewport_height=851,
           device_pixel_ratio=2.75, physical_size_inches=6.67,
           html5_features={"touch": True, "webgl": True, "webrtc": True,
                           "geolocation": True, "service_worker": True,
                           "local_storage": True},
           css_features={"hover": False, "pointer": "coarse", "any-hover": False,
                         "any-pointer": "coarse", "color-gamut": "srgb",
                         "prefers-color-scheme": "light",
                         "prefers-reduced-motion": "no-preference",
                         "prefers-contrast": "no-preference"},
           tags=["xiaomi", "android", "redmi", "amoled"],
           notes="Dispositivo principal del usuario"),
    
    Device(id="iphone-15", name="iPhone 15", category="phone",
           vendor="Apple", model="iPhone 15",
           viewport_width=390, viewport_height=844,
           device_pixel_ratio=3.0, physical_size_inches=6.1,
           html5_features={"touch": True, "webgl": True, "webrtc": True,
                           "geolocation": True, "service_worker": True,
                           "local_storage": True},
           tags=["apple", "ios", "iphone"]),
    
    Device(id="samsung-s24", name="Samsung Galaxy S24", category="phone",
           vendor="Samsung", model="Galaxy S24",
           viewport_width=393, viewport_height=873,
           device_pixel_ratio=2.75, physical_size_inches=6.2,
           tags=["samsung", "android", "galaxy"]),
    
    Device(id="pixel-8", name="Google Pixel 8", category="phone",
           vendor="Google", model="Pixel 8",
           viewport_width=412, viewport_height=915,
           device_pixel_ratio=2.625, physical_size_inches=6.2,
           tags=["google", "android", "pixel"]),
    
    # Tablets
    Device(id="ipad-air", name="iPad Air", category="tablet",
           vendor="Apple", model="iPad Air (5ª gen)",
           viewport_width=820, viewport_height=1180,
           device_pixel_ratio=2.0, physical_size_inches=10.9,
           html5_features={"touch": True, "webgl": True, "webrtc": True,
                           "geolocation": True, "service_worker": True,
                           "local_storage": True},
           tags=["apple", "ios", "ipad"]),
    
    Device(id="ipad-mini", name="iPad Mini", category="tablet",
           vendor="Apple", model="iPad Mini (6ª gen)",
           viewport_width=744, viewport_height=1133,
           device_pixel_ratio=2.0, physical_size_inches=8.3,
           tags=["apple", "ios", "ipad"]),
    
    Device(id="samsung-tab-s9", name="Samsung Galaxy Tab S9", category="tablet",
           vendor="Samsung", model="Galaxy Tab S9",
           viewport_width=820, viewport_height=1180,
           device_pixel_ratio=2.0, physical_size_inches=11.0,
           tags=["samsung", "android", "tablet"]),
    
    # Desktop
    Device(id="macbook-pro-14", name="MacBook Pro 14\"", category="desktop",
           vendor="Apple", model="MacBook Pro 14\"",
           viewport_width=1512, viewport_height=982,
           device_pixel_ratio=2.0, physical_size_inches=14.2,
           tags=["apple", "macos", "laptop", "retina"]),
    
    Device(id="macbook-pro-16", name="MacBook Pro 16\"", category="desktop",
           vendor="Apple", model="MacBook Pro 16\"",
           viewport_width=1728, viewport_height=1117,
           device_pixel_ratio=2.0, physical_size_inches=16.2,
           tags=["apple", "macos", "laptop", "retina"]),
    
    Device(id="desktop-1080p", name="Desktop 1080p", category="desktop",
           vendor="Generic", model="1920x1080",
           viewport_width=1920, viewport_height=1080,
           device_pixel_ratio=1.0,
           tags=["generic", "desktop", "1080p"]),
    
    Device(id="desktop-1440p", name="Desktop 1440p", category="desktop",
           vendor="Generic", model="2560x1440",
           viewport_width=2560, viewport_height=1440,
           device_pixel_ratio=1.0,
           tags=["generic", "desktop", "1440p"]),
    
    # Relojes
    Device(id="apple-watch-ultra", name="Apple Watch Ultra", category="watch",
           vendor="Apple", model="Watch Ultra",
           viewport_width=205, viewport_height=251,
           device_pixel_ratio=3.0, physical_size_inches=1.9,
           html5_features={"touch": True, "webgl": False, "webrtc": False,
                           "geolocation": True, "service_worker": False,
                           "local_storage": False},
           css_features={"hover": False, "pointer": "coarse", "any-hover": False,
                         "any-pointer": "coarse", "color-gamut": "srgb",
                         "prefers-color-scheme": "dark",
                         "prefers-reduced-motion": "no-preference",
                         "prefers-contrast": "more"},
           tags=["apple", "watchos", "wearable"]),
    
    # TV
    Device(id="apple-tv-4k", name="Apple TV 4K", category="tv",
           vendor="Apple", model="Apple TV 4K",
           viewport_width=1920, viewport_height=1080,
           device_pixel_ratio=1.0,
           html5_features={"touch": False, "webgl": True, "webrtc": False,
                           "geolocation": False, "service_worker": False,
                           "local_storage": True},
           css_features={"hover": False, "pointer": "coarse", "any-hover": False,
                         "any-pointer": "coarse", "color-gamut": "p3",
                         "prefers-color-scheme": "dark",
                         "prefers-reduced-motion": "no-preference",
                         "prefers-contrast": "more"},
           tags=["apple", "tvos", "tv"]),
]


def seed_default_devices():
    """Inserta dispositivos por defecto si la DB está vacía."""
    conn = get_db()
    count = conn.execute("SELECT COUNT(*) FROM devices").fetchone()[0]
    if count > 0:
        conn.close()
        return
    for dev in DEFAULT_DEVICES:
        add_device(dev)
    conn.close()


# ─── Utilidades de testing visual ──────────────────────────────

def simulate_viewport(device_id: str, image_path: str) -> dict:
    """
    Simula cómo se vería una imagen en un dispositivo específico.
    Calcula el escalado y recorte necesarios.
    
    Args:
        device_id: ID del dispositivo
        image_path: Ruta a la imagen
    
    Returns:
        Dict con información de simulación
    """
    from PIL import Image
    
    device = get_device(device_id)
    if not device:
        return {"error": f"Dispositivo '{device_id}' no encontrado"}
    
    try:
        img = Image.open(image_path)
        orig_w, orig_h = img.size
        
        # Calcular escalado para llenar el viewport
        vw, vh = device.viewport_width, device.viewport_height
        dpr = device.device_pixel_ratio
        
        scale_x = vw / orig_w
        scale_y = vh / orig_h
        fill_scale = max(scale_x, scale_y)
        fit_scale = min(scale_x, scale_y)
        
        return {
            "device": device.name,
            "viewport": f"{vw}x{vh}",
            "dpr": dpr,
            "screen_pixels": f"{int(vw * dpr)}x{int(vh * dpr)}",
            "original_size": f"{orig_w}x{orig_h}",
            "fill_scale": round(fill_scale, 3),
            "fit_scale": round(fit_scale, 3),
            "aspect_ratio_device": round(vw / vh, 3),
            "aspect_ratio_image": round(orig_w / orig_h, 3),
            "fits_perfectly": abs((vw / vh) - (orig_w / orig_h)) < 0.01,
            "is_landscape": vw > vh,
            "simulated_css_width": vw,
            "simulated_css_height": vh,
        }
    except Exception as e:
        return {"error": str(e)}


# ─── CLI ───────────────────────────────────────────────────────

def cli():
    """Interfaz CLI simple."""
    import sys
    if len(sys.argv) < 2:
        print("🦁 Device DB CLI")
        print("Uso: python3 device_db.py <comando> [args]")
        print("\nComandos:")
        print("  list                    — Listar dispositivos")
        print("  search <filtro> <valor> — Buscar (category|vendor|tag)")
        print("  simulate <id> <imagen>  — Simular viewport")
        print("  seed                    — Poblar DB con defaults")
        return

    cmd = sys.argv[1]
    
    if cmd == "list":
        for d in list_all_devices():
            print(f"  [{d.category:8}] {d.name:25s} {d.viewport_width:5d}x{d.viewport_height:<5d}"
                  f" ({d.device_pixel_ratio}x) {d.vendor}")
    
    elif cmd == "search":
        if len(sys.argv) < 4:
            print("Uso: device_db.py search <filtro> <valor>")
            return
        filtro, valor = sys.argv[2], sys.argv[3]
        kwargs = {filtro: valor}
        results = search_devices(**kwargs)
        for d in results:
            print(f"  [{d.category:8}] {d.name:25s} {d.viewport_width}x{d.viewport_height} ({d.vendor})")
        if not results:
            print("  Sin resultados")
    
    elif cmd == "simulate":
        if len(sys.argv) < 4:
            print("Uso: device_db.py simulate <device_id> <imagen>")
            return
        result = simulate_viewport(sys.argv[2], sys.argv[3])
        for k, v in result.items():
            print(f"  {k}: {v}")
    
    elif cmd == "seed":
        seed_default_devices()
        print(f"✅ Dispositivos por defecto insertados ({len(DEFAULT_DEVICES)} dispositivos)")


if __name__ == "__main__":
    cli()
