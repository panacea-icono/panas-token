#!/bin/bash

# Script para configurar aplicación Heroku para PANAS Token
# Uso: ./setup_heroku_app.sh [nombre-app-opcional]

set -e

echo "=== Configurando aplicación Heroku para PANAS Token ==="

# Usar nombre proporcionado o generar uno único
APP_NAME=${1:-"panas-token-$(date +%m%d%H%M)"}

echo "📱 Creando aplicación Heroku: $APP_NAME"

# Crear aplicación
heroku create $APP_NAME

echo "✅ Aplicación creada: $APP_NAME"

# Obtener la URL de la aplicación
APP_URL=$(heroku info -a $APP_NAME --json | jq -r '.app.web_url')
echo "🌐 URL de la aplicación: $APP_URL"

# Agregar PostgreSQL
echo "🗄️ Agregando PostgreSQL..."
heroku addons:create heroku-postgresql:mini -a $APP_NAME

# Agregar Redis
echo "🔄 Agregando Redis..."
heroku addons:create heroku-redis:mini -a $APP_NAME

# Esperar a que los addons estén listos
echo "⏳ Esperando a que los addons estén listos..."
sleep 30

# Configurar variables de entorno
echo "⚙️ Configurando variables de entorno..."

# Variables básicas
heroku config:set -a $APP_NAME \
  ENVIRONMENT="production" \
  SECRET_KEY="$(openssl rand -base64 32)" \
  CORS_ORIGINS="$APP_URL" \
  LOG_LEVEL="INFO"

# Variables de Algorand (ejemplos - debes configurar las reales)
heroku config:set -a $APP_NAME \
  ALGORAND_NODE_URL="https://testnet-api.algonode.cloud" \
  ALGORAND_INDEXER_URL="https://testnet-idx.algonode.cloud" \
  ALGORAND_NETWORK="testnet"

# Variables de OpenAI (debes configurar tu API key real)
echo "⚠️  IMPORTANTE: Configura tu OpenAI API Key:"
echo "heroku config:set -a $APP_NAME OPENAI_API_KEY=tu_api_key_aqui"

# Variables de Panacea (debes configurar las reales)
echo "⚠️  IMPORTANTE: Configura las variables de Panacea:"
echo "heroku config:set -a $APP_NAME PANACEA_API_URL=tu_url_panacea_aqui"
echo "heroku config:set -a $APP_NAME PANACEA_API_KEY=tu_api_key_panacea_aqui"

# Obtener información de la base de datos
echo "📊 Información de la base de datos:"
heroku config:get DATABASE_URL -a $APP_NAME

# Crear archivo de configuración local para referencia
cat > heroku_app_info.txt << EOF
Aplicación Heroku: $APP_NAME
URL: $APP_URL
Fecha de creación: $(date)

Para conectar esta aplicación localmente:
heroku git:remote -a $APP_NAME

Para ver logs:
heroku logs --tail -a $APP_NAME

Para ver variables de entorno:
heroku config -a $APP_NAME

Para acceder a la base de datos:
heroku pg:psql -a $APP_NAME

Para hacer deploy:
git push heroku main

Para ejecutar migraciones:
heroku run ./heroku_migrate.sh -a $APP_NAME
EOF

echo "✅ Configuración completada!"
echo "📄 Información guardada en heroku_app_info.txt"
echo ""
echo "🚀 Próximos pasos:"
echo "1. Configurar las API keys requeridas (OpenAI, Panacea)"
echo "2. Ejecutar: git push heroku main"
echo "3. Ejecutar: heroku run ./heroku_migrate.sh -a $APP_NAME"
echo "4. Verificar: heroku open -a $APP_NAME"
