#!/bin/bash

# Script para corregir automáticamente errores de formato en PANAS Token
# Uso: ./fix_formatting.sh

set -e

echo "🛠️  PANAS Token - Auto Format & Fix Script"
echo "=========================================="

cd /Users/kuchimac/panas_token/panas_token

# Función para corregir archivos Python
fix_python_files() {
    echo "🐍 Fixing Python files..."
    
    # Lista de archivos Python a corregir
    python_files=(
        "main.py"
        "openai_integration.py" 
        "panacea_integration.py"
        "openai_integration_fixed.py"
        "panacea_example.py"
    )
    
    for file in "${python_files[@]}"; do
        if [[ -f "$file" ]]; then
            echo "  📝 Fixing: $file"
            
            # Usar autopep8 si está disponible
            if command -v autopep8 &> /dev/null; then
                autopep8 --in-place --max-line-length=100 --aggressive --aggressive "$file"
            fi
            
            # Usar black si está disponible
            if command -v black &> /dev/null; then
                black --line-length=100 "$file" 2>/dev/null || true
            fi
            
            echo "  ✅ Fixed: $file"
        else
            echo "  ⚠️  File not found: $file"
        fi
    done
}

# Función para corregir imports no utilizados
fix_unused_imports() {
    echo ""
    echo "📦 Fixing unused imports..."
    
    # Usar autoflake si está disponible
    if command -v autoflake &> /dev/null; then
        autoflake --in-place --remove-all-unused-imports --remove-unused-variables \
                  main.py openai_integration.py panacea_integration.py 2>/dev/null || true
    fi
}

# Función para corregir whitespace
fix_whitespace() {
    echo ""
    echo "🧹 Fixing whitespace issues..."
    
    # Remover trailing whitespace
    for file in *.py; do
        if [[ -f "$file" ]]; then
            sed -i '' 's/[[:space:]]*$//' "$file"
        fi
    done
    
    echo "  ✅ Whitespace fixed"
}

# Función para instalar herramientas de formato si no están disponibles
install_formatting_tools() {
    echo ""
    echo "🔧 Installing formatting tools..."
    
    # Verificar e instalar herramientas
    tools_needed=false
    
    if ! command -v autopep8 &> /dev/null; then
        echo "  📦 Installing autopep8..."
        pip3 install autopep8 || poetry add --group dev autopep8 || true
        tools_needed=true
    fi
    
    if ! command -v black &> /dev/null; then
        echo "  📦 Installing black..."
        pip3 install black || poetry add --group dev black || true
        tools_needed=true
    fi
    
    if ! command -v autoflake &> /dev/null; then
        echo "  📦 Installing autoflake..."
        pip3 install autoflake || poetry add --group dev autoflake || true
        tools_needed=true
    fi
    
    if ! command -v isort &> /dev/null; then
        echo "  📦 Installing isort..."
        pip3 install isort || poetry add --group dev isort || true
        tools_needed=true
    fi
    
    if [ "$tools_needed" = false ]; then
        echo "  ✅ All formatting tools already available"
    fi
}

# Función para corregir imports con isort
fix_import_order() {
    echo ""
    echo "📚 Fixing import order..."
    
    if command -v isort &> /dev/null; then
        isort --profile black --line-length 100 *.py 2>/dev/null || true
        echo "  ✅ Import order fixed"
    else
        echo "  ⚠️  isort not available, skipping import order fix"
    fi
}

# Función para corregir problemas específicos encontrados
fix_specific_issues() {
    echo ""
    echo "🎯 Fixing specific issues..."
    
    # Corregir redefinición de datetime en panacea_integration.py
    if [[ -f "panacea_integration.py" ]]; then
        # Remover import duplicado de datetime
        sed -i '' '/^from datetime import datetime$/d' panacea_integration.py
        echo "  ✅ Fixed datetime redefinition in panacea_integration.py"
    fi
    
    # Corregir problemas de indentación
    for file in *.py; do
        if [[ -f "$file" ]]; then
            # Convertir tabs a espacios
            sed -i '' 's/\t/    /g' "$file"
        fi
    done
    
    echo "  ✅ Specific issues fixed"
}

# Función para validar después de las correcciones
validate_fixes() {
    echo ""
    echo "✅ Validating fixes..."
    
    # Verificar sintaxis Python
    for file in *.py; do
        if [[ -f "$file" ]]; then
            if python3 -m py_compile "$file" 2>/dev/null; then
                echo "  ✅ $file syntax OK"
            else
                echo "  ❌ $file still has syntax errors"
            fi
        fi
    done
}

# Ejecutar las correcciones
echo "🚀 Starting auto-fix process..."

install_formatting_tools
fix_specific_issues
fix_unused_imports
fix_import_order
fix_whitespace
fix_python_files
validate_fixes

echo ""
echo "🎉 Auto-fix completed!"
echo ""
echo "📋 Next steps to resolve VS Code 'undefined' errors:"
echo "1. Restart VS Code: Cmd+Shift+P -> 'Developer: Reload Window'"
echo "2. Check Python interpreter: Cmd+Shift+P -> 'Python: Select Interpreter'"
echo "3. Restart language servers: Cmd+Shift+P -> 'Developer: Restart Extension Host'"
echo "4. Clear VS Code cache: Close VS Code, delete ~/.vscode* folders, restart"
echo ""
echo "🔍 If 'undefined' errors persist:"
echo "• Check VS Code extensions (Python, Pylance, YAML, Docker)"
echo "• Verify workspace settings in .vscode/settings.json"
echo "• Check file encodings are UTF-8"
echo "• Ensure Poetry environment is activated"
echo ""
echo "🌟 To commit the fixes:"
echo "git add ."
echo "git commit -m '🛠️ Fix formatting and linting issues'"
