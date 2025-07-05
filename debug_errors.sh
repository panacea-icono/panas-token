#!/bin/bash

# Script para debuggear errores en el proyecto PANAS Token
# Uso: ./debug_errors.sh

set -e

echo "🔍 PANAS Token - Debugging Script"
echo "================================="

# Función para mostrar errores por archivo
check_file_errors() {
    local file="$1"
    local description="$2"

    echo ""
    echo "📄 Checking $description: $(basename "$file")"
    echo "-------------------------------------------"

    if [[ ! -f "$file" ]]; then
        echo "❌ File not found: $file"
        return 1
    fi

    # Verificar sintaxis Python
    if [[ "$file" == *.py ]]; then
        echo "🐍 Python syntax check..."
        if python3 -m py_compile "$file" 2>/dev/null; then
            echo "✅ Python syntax OK"
        else
            echo "❌ Python syntax error:"
            python3 -m py_compile "$file"
        fi

        # Verificar con flake8 si está disponible
        if command -v flake8 &> /dev/null; then
            echo "🔍 Flake8 check..."
            flake8 "$file" --max-line-length=100 --ignore=E501,W503 || true
        fi
    fi

    # Verificar sintaxis YAML
    if [[ "$file" == *.yaml ]] || [[ "$file" == *.yml ]]; then
        echo "📝 YAML syntax check..."
        if command -v yamllint &> /dev/null; then
            yamllint "$file" || true
        elif python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null; then
            echo "✅ YAML syntax OK"
        else
            echo "❌ YAML syntax error:"
            python3 -c "import yaml; yaml.safe_load(open('$file'))"
        fi
    fi

    # Verificar sintaxis shell script
    if [[ "$file" == *.sh ]]; then
        echo "🐚 Shell script check..."
        if command -v shellcheck &> /dev/null; then
            shellcheck "$file" || true
        elif bash -n "$file" 2>/dev/null; then
            echo "✅ Shell syntax OK"
        else
            echo "❌ Shell syntax error:"
            bash -n "$file"
        fi
    fi

    # Verificar Dockerfile
    if [[ "$(basename "$file")" == "Dockerfile" ]]; then
        echo "🐳 Dockerfile check..."
        if command -v hadolint &> /dev/null; then
            hadolint "$file" || true
        else
            echo "ℹ️  hadolint not available, skipping Dockerfile linting"
        fi
    fi
}

# Lista de archivos principales para verificar
FILES_TO_CHECK=(
    "/Users/kuchimac/panas_token/panas_token/main.py:FastAPI Backend"
    "/Users/kuchimac/panas_token/panas_token/openai_integration.py:OpenAI Integration"
    "/Users/kuchimac/panas_token/panas_token/panacea_integration.py:Panacea Integration"
    "/Users/kuchimac/panas_token/panas_token/Dockerfile:Docker Configuration"
    "/Users/kuchimac/panas_token/panas_token/docker-compose.yml:Docker Compose"
    "/Users/kuchimac/panas_token/panas_token/deploy_docker.sh:Docker Deploy Script"
    "/Users/kuchimac/panas_token/panas_token/deploy_heroku.sh:Heroku Deploy Script"
    "/Users/kuchimac/panas_token/panas_token/fix_deployment_issues.sh:Fix Deploy Script"
    "/Users/kuchimac/panas_token/panas_token/.github/workflows/panas_token-contracts-ci.yaml:Contracts CI"
    "/Users/kuchimac/panas_token/panas_token/.github/workflows/panas_token-contracts-cd.yaml:Contracts CD"
    "/Users/kuchimac/panas_token/panas_token/.github/workflows/panas_token-frontend-ci.yaml:Frontend CI"
    "/Users/kuchimac/panas_token/panas_token/.github/workflows/panas_token-frontend-cd.yaml:Frontend CD"
    "/Users/kuchimac/panas_token/panas_token/.github/workflows/release.yaml:Release Workflow"
)

echo "🚀 Starting comprehensive error check..."

# Verificar cada archivo
for entry in "${FILES_TO_CHECK[@]}"; do
    IFS=":" read -r filepath description <<< "$entry"
    check_file_errors "$filepath" "$description"
done

echo ""
echo "🔧 Environment and Dependencies Check"
echo "====================================="

# Verificar Python
echo "🐍 Python version:"
python3 --version || echo "❌ Python3 not found"

# Verificar Poetry
echo ""
echo "📦 Poetry check:"
if command -v poetry &> /dev/null; then
    echo "✅ Poetry available: $(poetry --version)"
    echo "📋 Poetry dependencies check:"
    cd /Users/kuchimac/panas_token/panas_token
    poetry check || echo "⚠️  Poetry check failed"
else
    echo "❌ Poetry not found"
fi

# Verificar Docker
echo ""
echo "🐳 Docker check:"
if command -v docker &> /dev/null; then
    echo "✅ Docker available: $(docker --version)"
else
    echo "❌ Docker not found"
fi

# Verificar Git
echo ""
echo "📚 Git status:"
if git status &> /dev/null; then
    echo "✅ Git repository OK"
    echo "📊 Git status:"
    git status --porcelain | head -10
else
    echo "❌ Git repository issues"
fi

echo ""
echo "🎯 Common Issues and Solutions"
echo "============================="
echo "1. 'undefined' errors in VS Code:"
echo "   - Restart VS Code"
echo "   - Check language server extensions"
echo "   - Verify file encodings"
echo ""
echo "2. Python import errors:"
echo "   - Activate Poetry environment: poetry shell"
echo "   - Install dependencies: poetry install"
echo "   - Check PYTHONPATH"
echo ""
echo "3. YAML workflow errors:"
echo "   - Check indentation (spaces, not tabs)"
echo "   - Validate GitHub Actions syntax"
echo "   - Check required secrets in GitHub"
echo ""
echo "4. Docker errors:"
echo "   - Check Dockerfile syntax"
echo "   - Verify base image availability"
echo "   - Check .dockerignore patterns"
echo ""
echo "✅ Debugging complete!"
echo ""
echo "🔧 To fix 'undefined' errors, try:"
echo "   1. Restart VS Code: Ctrl+Shift+P -> Developer: Reload Window"
echo "   2. Check Python interpreter: Ctrl+Shift+P -> Python: Select Interpreter"
echo "   3. Restart language servers: Ctrl+Shift+P -> Developer: Restart Extension Host"
