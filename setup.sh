#!/usr/bin/env bash
# 🦁 setup.sh — Samson Vision installer
# Uso: bash setup.sh [--dev]
#   --dev: también instala opencv-python-headless y pytesseract
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

echo "🦁 Samson Vision — Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━"

# 1. Crear directorios de trabajo
echo "📁 Creando directorios..."
mkdir -p input output

# 2. Enlazar assets desde PUBLIC/ (o copiar si no hay symlink)
if [ ! -d assets ]; then
    if [ -d PUBLIC/assets ]; then
        cp -r PUBLIC/assets assets
        echo "   assets/ → copiado desde PUBLIC/assets/"
    else
        mkdir -p assets
        echo "   assets/ → creado vacío"
    fi
fi

# 3. Venv
if [ ! -d .venv ]; then
    echo "🐍 Creando venv..."
    python3 -m venv .venv
fi
source .venv/bin/activate

# 4. Dependencias mínimas
echo "📦 Instalando dependencias..."
pip install --quiet --upgrade pip
pip install pillow numpy

# 5. Dependencias opcionales (--dev)
if [ "${1:-}" = "--dev" ]; then
    echo "📦 Instalando extras de desarrollo..."
    pip install opencv-python-headless pytesseract
fi

# 6. Instalar el paquete en modo editable
echo "📦 Instalando paquete..."
pip install -e .

# 7. Verificar
echo "🔍 Verificando instalación..."
python3 -c "from samson_core import __version__; print(f'   Samson Vision v{__version__} ✅')"

# 8. Tests
echo "🧪 Ejecutando tests..."
python3 test/run_tests.py

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Samson Vision listo"
echo ""
echo "   Uso rápido:"
echo "     source .venv/bin/activate"
echo "     samson-vision assets/samson_pillars_crumbling.png --md"
echo ""
echo "   O desde Python:"
echo "     from samson_vision import generate_svp"
echo "     svp = generate_svp('assets/samson_pillars_crumbling.png', fmt='md')"
echo ""
