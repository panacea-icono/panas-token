#!/bin/bash

# 🛠️ PANAS Token - CLI Tools Installation Script
# Este script instala todas las herramientas CLI necesarias para el desarrollo

set -e  # Exit on any error

echo "🚀 Instalando herramientas CLI para PANAS Token..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar si Homebrew está instalado
check_homebrew() {
    if command -v brew &> /dev/null; then
        log_success "Homebrew ya está instalado"
    else
        log_info "Instalando Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        log_success "Homebrew instalado"
    fi
}

# Verificar si Node.js está instalado
check_nodejs() {
    if command -v node &> /dev/null; then
        log_success "Node.js ya está instalado: $(node --version)"
    else
        log_error "Node.js no está instalado. Por favor instala Node.js primero."
        exit 1
    fi
}

# Verificar si Poetry está instalado
check_poetry() {
    if command -v poetry &> /dev/null; then
        log_success "Poetry ya está instalado: $(poetry --version)"
    else
        log_info "Instalando Poetry..."
        curl -sSL https://install.python-poetry.org | python3 -
        log_success "Poetry instalado"
    fi
}

# Instalar Docker CLI
install_docker_cli() {
    log_info "Verificando Docker CLI..."
    if command -v docker &> /dev/null; then
        log_success "Docker CLI ya está instalado: $(docker --version)"
    else
        log_info "Instalando Docker CLI..."
        brew install docker
        log_success "Docker CLI instalado"
    fi
}

# Instalar Heroku CLI
install_heroku_cli() {
    log_info "Verificando Heroku CLI..."
    if command -v heroku &> /dev/null; then
        log_success "Heroku CLI ya está instalado: $(heroku --version)"
    else
        log_info "Instalando Heroku CLI..."
        brew tap heroku/brew && brew install heroku
        log_success "Heroku CLI instalado"
    fi
}

# Instalar Vercel CLI
install_vercel_cli() {
    log_info "Verificando Vercel CLI..."
    if command -v vercel &> /dev/null; then
        log_success "Vercel CLI ya está instalado: $(vercel --version)"
    else
        log_info "Instalando Vercel CLI..."
        npm install -g vercel
        log_success "Vercel CLI instalado"
    fi
}

# Instalar GitHub CLI
install_github_cli() {
    log_info "Verificando GitHub CLI..."
    if command -v gh &> /dev/null; then
        log_success "GitHub CLI ya está instalado: $(gh --version | head -1)"
    else
        log_info "Instalando GitHub CLI..."
        brew install gh
        log_success "GitHub CLI instalado"
    fi
}

# Instalar AlgoKit CLI
install_algokit_cli() {
    log_info "Verificando AlgoKit CLI..."
    if command -v algokit &> /dev/null; then
        log_success "AlgoKit CLI ya está instalado: $(algokit --version)"
    else
        log_info "Instalando AlgoKit CLI..."
        brew install algorandfoundation/tap/algokit
        log_success "AlgoKit CLI instalado"
    fi
}

# Instalar Hugging Face CLI
install_huggingface_cli() {
    log_info "Verificando Hugging Face CLI..."
    if pip list | grep -q huggingface-hub; then
        log_success "Hugging Face Hub ya está instalado"
    else
        log_info "Instalando Hugging Face CLI..."
        pip install --upgrade huggingface_hub[cli]
        log_success "Hugging Face CLI instalado"
    fi
}

# Configurar variables de entorno
setup_environment() {
    log_info "Configurando variables de entorno..."

    if [ -f ".env" ]; then
        log_success "Archivo .env ya existe"
    else
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log_success "Archivo .env creado desde .env.example"
        elif [ -f ".env copy" ]; then
            cp ".env copy" .env
            log_success "Archivo .env creado desde .env copy"
        else
            log_warning "No se encontró archivo .env.example o .env copy"
        fi
    fi
}

# Función principal
main() {
    echo "🎯 Iniciando instalación de herramientas CLI..."
    echo ""

    # Verificaciones previas
    check_homebrew
    check_nodejs
    check_poetry

    echo ""
    echo "📦 Instalando herramientas CLI..."

    # Instalaciones
    install_docker_cli
    install_heroku_cli
    install_vercel_cli
    install_github_cli
    install_algokit_cli
    install_huggingface_cli

    echo ""
    echo "⚙️ Configurando entorno..."
    setup_environment

    echo ""
    echo "✅ INSTALACIÓN COMPLETADA"
    echo ""
    echo "🎉 Todas las herramientas CLI han sido instaladas:"
    echo "   ✓ Docker CLI"
    echo "   ✓ Heroku CLI"
    echo "   ✓ Vercel CLI"
    echo "   ✓ GitHub CLI"
    echo "   ✓ AlgoKit CLI"
    echo "   ✓ Hugging Face CLI"
    echo ""
    echo "📝 Próximos pasos:"
    echo "   1. Configura tu archivo .env con las claves API necesarias"
    echo "   2. Autentícate en los servicios:"
    echo "      - heroku login"
    echo "      - vercel login"
    echo "      - gh auth login"
    echo "      - huggingface-cli login"
    echo "   3. Ejecuta 'poetry shell' para activar el entorno Python"
    echo ""
}

# Ejecutar función principal
main "$@"
