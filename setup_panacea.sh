#!/bin/bash
"""
Script de inicialización para Panacea API Central
Clona y configura el repositorio de Panacea
"""

set -e

echo "🏥 Inicializando Panacea API Central..."

# Directorio de trabajo
PANACEA_DIR="./panacea-api-central-repo"
GITHUB_REPO="https://github.com/panacea-icono/panacea-api-central.git"

# Función para logging
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Clonar repositorio si no existe
if [ ! -d "$PANACEA_DIR" ]; then
    log "Clonando repositorio Panacea API Central..."
    git clone "$GITHUB_REPO" "$PANACEA_DIR"
else
    log "Repositorio ya existe, actualizando..."
    cd "$PANACEA_DIR"
    git pull origin main
    cd ..
fi

# Verificar estructura del repositorio
if [ -d "$PANACEA_DIR" ]; then
    log "✅ Repositorio Panacea clonado exitosamente"
    
    # Mostrar información del repositorio
    cd "$PANACEA_DIR"
    COMMIT_HASH=$(git rev-parse HEAD)
    COMMIT_DATE=$(git log -1 --format=%cd --date=short)
    BRANCH=$(git branch --show-current)
    
    log "📊 Información del repositorio:"
    log "  - Branch: $BRANCH"
    log "  - Último commit: $COMMIT_HASH"
    log "  - Fecha: $COMMIT_DATE"
    
    # Listar archivos principales
    log "📁 Archivos principales encontrados:"
    find . -maxdepth 2 -name "*.py" -o -name "*.md" -o -name "requirements.txt" -o -name "Dockerfile" | head -10
    
    cd ..
else
    log "❌ Error: No se pudo clonar el repositorio"
    exit 1
fi

# Crear configuración de integración
log "⚙️ Creando configuración de integración..."

cat > "./panacea-central/config.json" << EOF
{
  "repository": {
    "url": "$GITHUB_REPO",
    "local_path": "$PANACEA_DIR",
    "last_update": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  },
  "integration": {
    "panas_token_api": "http://panas-api:8000",
    "medical_gpt_api": "http://medical-gpt-api:5003",
    "telegram_bots": "http://telegram-bots:8080",
    "nfd_domains": [
      "10.panas.algo",
      "tokenizado.algo", 
      "panacea.icono.algo",
      "activo.algo"
    ]
  },
  "services": {
    "health_check_interval": 30,
    "sync_interval": 300,
    "retry_attempts": 3
  }
}
EOF

# Crear script de healthcheck
cat > "./panacea-central/healthcheck.py" << 'EOF'
#!/usr/bin/env python3
import asyncio
import aiohttp
import json
from datetime import datetime

async def check_panacea_health():
    """Verificar salud de Panacea API Central"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://panacea-api-central:8000/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Panacea API Central: {data}")
                    return True
                else:
                    print(f"❌ Panacea API Central error: {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Error conectando con Panacea: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(check_panacea_health())
    exit(0 if result else 1)
EOF

chmod +x "./panacea-central/healthcheck.py"

log "✅ Configuración completada"
log "🚀 Para iniciar los servicios ejecuta: docker compose up -d"
log "🔍 Para verificar estado: python ./panacea-central/healthcheck.py"

echo ""
echo "📋 Resumen de integración Panacea:"
echo "  - Repositorio: $GITHUB_REPO"
echo "  - Directorio local: $PANACEA_DIR"
echo "  - Configuración: ./panacea-central/config.json"
echo "  - Healthcheck: ./panacea-central/healthcheck.py"
echo "  - Comandos Telegram: /panacea, /sync, /activos, /historial"
echo ""
