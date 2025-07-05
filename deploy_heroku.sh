#!/bin/bash

# Script de deployment para Heroku
# Uso: ./deploy_heroku.sh [app-name]

set -e

# Generar nombre único si no se proporciona
if [ -z "$1" ]; then
    TIMESTAMP=$(date +%s)
    APP_NAME="panas-token-api-${TIMESTAMP}"
else
    APP_NAME="$1"
fi

echo "🚀 Deploying PANAS Token API to Heroku: $APP_NAME"

# Verificar que el nombre sea válido para Heroku
if [[ ! "$APP_NAME" =~ ^[a-z][a-z0-9-]*[a-z0-9]$ ]] || [ ${#APP_NAME} -gt 30 ]; then
    echo "❌ Nombre de app inválido: $APP_NAME"
    echo "💡 El nombre debe:"
    echo "   - Comenzar con una letra minúscula"
    echo "   - Contener solo letras minúsculas, números y guiones"
    echo "   - Terminar con una letra o número"
    echo "   - Tener máximo 30 caracteres"
    exit 1
fi

# Verificar que Heroku CLI esté instalado
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI no está instalado. Instalando..."
    brew tap heroku/brew && brew install heroku
fi

# Login a Heroku (si no está logueado)
echo "🔐 Verificando login de Heroku..."
if ! heroku auth:whoami &> /dev/null; then
    echo "🔑 Iniciando login en Heroku..."
    heroku login
fi

# Crear app si no existe
echo "📱 Verificando/creando app de Heroku..."
if ! heroku apps:info $APP_NAME &> /dev/null; then
    echo "Creating new Heroku app: $APP_NAME"
    heroku create $APP_NAME
else
    echo "App $APP_NAME already exists"
fi

# Configurar variables de entorno
echo "⚙️ Configurando variables de entorno..."
heroku config:set \
    HOST=0.0.0.0 \
    ALGORAND_NETWORK=testnet \
    PANAS_TOTAL_SUPPLY=1000000 \
    PANAS_DECIMALS=6 \
    PANAS_TOKEN_NAME=PANAS \
    PANAS_USE_CASE=medical_research_incentive \
    --app $APP_NAME

# Configurar buildpacks
echo "🔧 Configurando buildpacks..."
heroku buildpacks:clear --app $APP_NAME
heroku buildpacks:add heroku/python --app $APP_NAME

# Configurar add-ons (base de datos)
echo "�️ Configurando base de datos..."

# Configurar PostgreSQL
echo "🐘 Configurando PostgreSQL..."
if heroku addons:create heroku-postgresql:essential-0 --app $APP_NAME 2>/dev/null; then
    echo "✅ PostgreSQL essential-0 instalado"
elif heroku addons:create heroku-postgresql:mini --app $APP_NAME 2>/dev/null; then
    echo "✅ PostgreSQL mini instalado"
elif heroku addons:create heroku-postgresql:hobby-dev --app $APP_NAME 2>/dev/null; then
    echo "✅ PostgreSQL hobby-dev instalado"
else
    echo "⚠️ PostgreSQL addon ya existe o no disponible"
fi

# Configurar Redis
echo "🔴 Configurando Redis..."
if heroku addons:create heroku-redis:mini --app $APP_NAME 2>/dev/null; then
    echo "✅ Redis mini instalado"
elif heroku addons:create heroku-redis:hobby-dev --app $APP_NAME 2>/dev/null; then
    echo "✅ Redis hobby-dev instalado"
else
    echo "⚠️ Redis addon ya existe o no disponible"
fi

# Esperar que PostgreSQL esté listo
echo "⏳ Esperando que la base de datos esté lista..."
heroku pg:wait --app $APP_NAME 2>/dev/null || echo "PostgreSQL ready or not configured"

# Configurar git remote si no existe
if ! git remote get-url heroku &> /dev/null; then
    echo "📡 Configurando git remote..."
    heroku git:remote -a $APP_NAME
fi

# Deploy
echo "🚀 Desplegando a Heroku..."
git add .
git commit -m "Deploy PANAS Token API to Heroku" || echo "No changes to commit"
git push heroku main

# Verificar deployment
echo "✅ Verificando deployment..."
heroku ps --app $APP_NAME
heroku logs --tail --app $APP_NAME &

# Obtener URL de la app
APP_URL=$(heroku apps:info $APP_NAME --json | jq -r '.app.web_url')
echo "🌐 App desplegada en: $APP_URL"
echo "📖 Documentación API: ${APP_URL}docs"
echo "❤️ Health check: ${APP_URL}health"

echo "🎉 Deployment completado!"
echo ""
echo "Comandos útiles:"
echo "  heroku logs --tail --app $APP_NAME"
echo "  heroku ps --app $APP_NAME"
echo "  heroku config --app $APP_NAME"
echo "  heroku open --app $APP_NAME"
