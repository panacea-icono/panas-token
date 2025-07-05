#!/bin/bash

# 🐍 PANAS Token - Poetry Shell Activation Script
# Este script activa el entorno virtual de Poetry y configura el shell

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Activando entorno Poetry para PANAS Token...${NC}"

# Verificar si estamos en el directorio correcto
if [ ! -f "pyproject.toml" ]; then
    echo -e "${YELLOW}⚠️  No se encontró pyproject.toml en el directorio actual${NC}"
    echo "Asegúrate de estar en el directorio raíz del proyecto"
    exit 1
fi

# Verificar si Poetry está instalado
if ! command -v poetry &> /dev/null; then
    echo -e "${YELLOW}⚠️  Poetry no está instalado${NC}"
    echo "Instala Poetry primero: curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

# Cargar variables de entorno si existe .env
if [ -f ".env" ]; then
    echo -e "${GREEN}✅ Cargando variables de entorno desde .env${NC}"
    export $(cat .env | grep -v '^#' | xargs)
else
    echo -e "${YELLOW}⚠️  No se encontró archivo .env${NC}"
    echo "Copia .env.example a .env y configura tus variables"
fi

# Mostrar información del entorno
echo -e "${GREEN}📦 Información del entorno Poetry:${NC}"
poetry env info

echo ""
echo -e "${GREEN}🎯 Comandos útiles:${NC}"
echo "  poetry show                 - Ver dependencias instaladas"
echo "  poetry add <package>        - Agregar nueva dependencia"
echo "  poetry remove <package>     - Remover dependencia"
echo "  poetry install              - Instalar dependencias"
echo "  poetry run python <script>  - Ejecutar script Python"
echo "  exit                        - Salir del entorno virtual"

echo ""
echo -e "${BLUE}🔥 Entorno Poetry activado. ¡Listo para desarrollar!${NC}"

# Activar el shell de Poetry
poetry shell
