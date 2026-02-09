#!/bin/bash

# Script para ejecutar la aplicación Word-Range Rewriter
# Navega a src, activa el venv e inicia la app

set -e  # Salir si hay error

echo "🚀 Word-Range Rewriter: Iniciando aplicación..."

# Cambiar a directorio src
cd src

# Verificar que venv existe
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment no encontrado en src/venv"
    echo "Creando virtual environment..."
    python3 -m venv venv
fi

# Activar virtual environment
echo "📦 Activando virtual environment..."
source venv/bin/activate

# Verificar que requirements están instalados
if [ ! -f "venv/lib/python3*/site-packages/flask" ]; then
    echo "📥 Instalando dependencias..."
    pip install -r requirements.txt
fi

# Verificar que .env existe
if [ ! -f ".env" ]; then
    echo "⚠️  Archivo .env no encontrado"
    echo "Creando .env a partir de .env.example..."
    cp .env.example .env
    echo "⚠️  Edita .env e ingresa tu OPENAI_API_KEY"
    echo "Por ahora, iniciando en modo limitado..."
fi

# Iniciar la aplicación
echo "✅ Iniciando servidor Flask..."
echo "📍 Accede a: http://127.0.0.1:5000"
echo ""

python app.py
