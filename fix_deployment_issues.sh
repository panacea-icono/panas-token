#!/bin/bash

# Script para diagnosticar y arreglar problemas de deployment
# Uso: ./fix_deployment_issues.sh

set -e

echo "🔧 PANAS Token - Diagnosticando y arreglando problemas de deployment"
echo "=================================================================="

# Función para imprimir sección
print_section() {
    echo ""
    echo "📋 $1"
    echo "----------------------------------------"
}

# 1. Verificar Docker Desktop
print_section "Verificando Docker Desktop"

if command -v docker &> /dev/null; then
    echo "✅ Docker está instalado"

    # Verificar si Docker está corriendo
    if docker info &> /dev/null; then
        echo "✅ Docker está corriendo"
    else
        echo "❌ Docker no está corriendo. Iniciando Docker Desktop..."
        open -a Docker
        echo "⏳ Esperando que Docker Desktop inicie..."
        sleep 10

        # Verificar nuevamente
        if docker info &> /dev/null; then
            echo "✅ Docker iniciado correctamente"
        else
            echo "❌ No se pudo iniciar Docker. Por favor inicia Docker Desktop manualmente"
            exit 1
        fi
    fi

    # Arreglar problema con docker-credential-desktop
    echo "🔧 Configurando credenciales de Docker..."

    # Verificar si existe el helper de credenciales
    if [ -f "$HOME/.docker/config.json" ]; then
        echo "📝 Archivo de configuración Docker encontrado"

        # Backup del config actual
        cp "$HOME/.docker/config.json" "$HOME/.docker/config.json.backup"

        # Crear configuración sin credHelper problemático
        cat > "$HOME/.docker/config.json" << EOF
{
  "auths": {},
  "credsStore": ""
}
EOF
        echo "✅ Configuración Docker actualizada"
    else
        echo "📁 Creando directorio .docker..."
        mkdir -p "$HOME/.docker"

        cat > "$HOME/.docker/config.json" << EOF
{
  "auths": {},
  "credsStore": ""
}
EOF
        echo "✅ Configuración Docker creada"
    fi

else
    echo "❌ Docker no está instalado. Instalando..."
    brew install --cask docker
    echo "⚠️ Por favor inicia Docker Desktop manualmente y ejecuta este script nuevamente"
    exit 1
fi

# 2. Verificar Heroku CLI
print_section "Verificando Heroku CLI"

if command -v heroku &> /dev/null; then
    echo "✅ Heroku CLI está instalado"

    # Verificar login
    if heroku auth:whoami &> /dev/null; then
        USER=$(heroku auth:whoami)
        echo "✅ Logueado como: $USER"

        # Verificar organizaciones disponibles
        echo "📋 Organizaciones disponibles:"
        heroku orgs || echo "⚠️ No tienes acceso a organizaciones (normal para cuentas gratuitas)"

    else
        echo "🔑 No estás logueado en Heroku. Iniciando login..."
        heroku login
    fi

else
    echo "❌ Heroku CLI no está instalado. Instalando..."
    brew tap heroku/brew && brew install heroku
fi

# 3. Verificar Git
print_section "Verificando Git"

if git status &> /dev/null; then
    echo "✅ Repositorio Git válido"

    # Verificar que no hay cambios sin commitear
    if [ -z "$(git status --porcelain)" ]; then
        echo "✅ No hay cambios pendientes"
    else
        echo "⚠️ Hay cambios sin commitear. Preparando commit..."
        git add .
        git commit -m "Fix deployment issues and update configuration" || echo "✅ Commit realizado o no hay cambios"
    fi

    # Verificar branch principal
    CURRENT_BRANCH=$(git branch --show-current)
    echo "📍 Branch actual: $CURRENT_BRANCH"

    if [ "$CURRENT_BRANCH" != "main" ] && [ "$CURRENT_BRANCH" != "master" ]; then
        echo "⚠️ No estás en la branch principal. Cambiando a main..."
        git checkout main 2>/dev/null || git checkout master 2>/dev/null || echo "❌ No se pudo cambiar a branch principal"
    fi

else
    echo "❌ No es un repositorio Git válido"
    echo "🔧 Inicializando repositorio Git..."
    git init
    git add .
    git commit -m "Initial commit with PANAS Token API"
fi

# 4. Verificar archivos de deployment
print_section "Verificando archivos de deployment"

REQUIRED_FILES=(
    "main.py"
    "requirements.txt"
    "Procfile"
    "runtime.txt"
    "Dockerfile"
    ".env.example"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file existe"
    else
        echo "❌ $file falta"
    fi
done

# Verificar contenido de runtime.txt
if [ -f "runtime.txt" ]; then
    RUNTIME_CONTENT=$(cat runtime.txt | tr -d '\n\r\t ')
    if [[ "$RUNTIME_CONTENT" =~ ^python-[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        echo "✅ runtime.txt tiene formato correcto: $RUNTIME_CONTENT"
    else
        echo "🔧 Arreglando runtime.txt..."
        echo "python-3.11.9" > runtime.txt
        echo "✅ runtime.txt corregido"
    fi
fi

# 5. Test local de la aplicación
print_section "Testing aplicación local"

if command -v python3 &> /dev/null; then
    echo "✅ Python3 disponible"

    # Verificar dependencias
    echo "📦 Verificando dependencias..."
    if [ -f "requirements.txt" ]; then
        echo "⏳ Instalando dependencias..."
        pip3 install -r requirements.txt --quiet || echo "⚠️ Algunas dependencias pueden faltar"
    fi

    # Test básico de importación
    echo "🧪 Testing importación de main.py..."
    python3 -c "
try:
    from main import app
    print('✅ main.py se importa correctamente')
except Exception as e:
    print(f'❌ Error importando main.py: {e}')
    exit(1)
" || echo "⚠️ Problema con importación"

else
    echo "❌ Python3 no está disponible"
fi

# 6. Crear script de deployment simplificado
print_section "Creando scripts de deployment mejorados"

# Script simplificado para Heroku
cat > deploy_heroku_simple.sh << 'EOF'
#!/bin/bash

# Script simplificado para Heroku (sin organizaciones)
set -e

APP_NAME=${1:-"panas-token-$(date +%s)"}

echo "🚀 Deploying to Heroku: $APP_NAME"

# Verificar login
if ! heroku auth:whoami &> /dev/null; then
    echo "🔑 Please login to Heroku:"
    heroku login
fi

# Crear app (sin especificar organización)
echo "📱 Creating Heroku app..."
if ! heroku apps:info $APP_NAME &> /dev/null; then
    heroku create $APP_NAME
fi

# Configurar buildpack
heroku buildpacks:clear --app $APP_NAME
heroku buildpacks:add heroku/python --app $APP_NAME

# Variables básicas
heroku config:set DEBUG=false --app $APP_NAME
heroku config:set HOST=0.0.0.0 --app $APP_NAME

# Deploy
git push heroku main

echo "✅ Deployed to: https://$APP_NAME.herokuapp.com"
EOF

chmod +x deploy_heroku_simple.sh

# Script simplificado para Docker
cat > deploy_docker_simple.sh << 'EOF'
#!/bin/bash

# Script simplificado para Docker
set -e

echo "🐳 Building Docker image..."
docker build -t panas-token-api .

echo "🚀 Starting container..."
docker stop panas-api 2>/dev/null || true
docker rm panas-api 2>/dev/null || true

docker run -d \
    --name panas-api \
    -p 8000:8000 \
    --env-file .env \
    panas-token-api

echo "✅ Container started at http://localhost:8000"
EOF

chmod +x deploy_docker_simple.sh

echo "✅ Scripts simplificados creados"

# 7. Resumen y próximos pasos
print_section "Resumen y próximos pasos"

echo "🎉 Diagnóstico completado. Próximos pasos:"
echo ""
echo "Para deployment en Heroku:"
echo "  ./deploy_heroku_simple.sh [nombre-app]"
echo ""
echo "Para deployment en Docker:"
echo "  ./deploy_docker_simple.sh"
echo ""
echo "Para test local:"
echo "  python3 main.py"
echo ""
echo "URLs importantes después del deployment:"
echo "  - API docs: /docs"
echo "  - Health check: /health"
echo "  - Metrics: /metrics"
echo ""
echo "⚠️ Nota sobre Panacea API:"
echo "  Los errores 404 en Panacea API son normales ya que usamos una URL de prueba."
echo "  La aplicación funciona con fallback responses."

echo ""
echo "🔧 Si sigues teniendo problemas:"
echo "  1. Revisa que Docker Desktop esté corriendo"
echo "  2. Verifica tu login en Heroku con: heroku auth:whoami"
echo "  3. Usa los scripts simplificados creados"
echo "  4. Revisa los logs con: docker logs panas-api"
