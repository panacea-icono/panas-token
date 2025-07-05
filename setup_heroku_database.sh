#!/bin/bash

# Script para configurar base de datos en Heroku
# Uso: ./setup_heroku_database.sh [app-name]

set -e

APP_NAME=${1:-"panas-token-api"}

echo "🗄️ Configurando Base de Datos en Heroku para: $APP_NAME"
echo "================================================="

# Verificar que Heroku CLI esté instalado
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI no está instalado."
    echo "💡 Instalar con: brew install heroku/brew/heroku"
    exit 1
fi

# Verificar login
if ! heroku auth:whoami &> /dev/null; then
    echo "❌ No estás logueado en Heroku"
    echo "🔑 Ejecuta: heroku login"
    exit 1
fi

# Verificar que la app existe
if ! heroku apps:info $APP_NAME &> /dev/null; then
    echo "❌ La app $APP_NAME no existe en Heroku"
    echo "💡 Crear primero con: heroku create $APP_NAME"
    exit 1
fi

echo "✅ App $APP_NAME encontrada"

# Función para configurar PostgreSQL
setup_postgresql() {
    echo ""
    echo "🐘 Configurando PostgreSQL..."

    # Verificar si PostgreSQL ya existe
    if heroku addons --app $APP_NAME | grep -q "heroku-postgresql"; then
        echo "✅ PostgreSQL ya está configurado"

        # Obtener información de la base de datos
        echo "📊 Información de PostgreSQL:"
        heroku pg:info --app $APP_NAME
    else
        echo "📦 Instalando PostgreSQL..."

        # Instalar PostgreSQL (plan básico gratuito)
        if heroku addons:create heroku-postgresql:essential-0 --app $APP_NAME; then
            echo "✅ PostgreSQL instalado exitosamente"
        elif heroku addons:create heroku-postgresql:mini --app $APP_NAME; then
            echo "✅ PostgreSQL mini instalado exitosamente"
        else
            echo "⚠️ Intentando con plan hobby-dev..."
            heroku addons:create heroku-postgresql:hobby-dev --app $APP_NAME
        fi

        echo "⏳ Esperando que PostgreSQL esté listo..."
        heroku pg:wait --app $APP_NAME
    fi

    # Obtener DATABASE_URL
    DATABASE_URL=$(heroku config:get DATABASE_URL --app $APP_NAME)
    if [ -n "$DATABASE_URL" ]; then
        echo "✅ DATABASE_URL configurada"
        echo "🔗 URL: ${DATABASE_URL:0:30}..."
    else
        echo "❌ No se pudo obtener DATABASE_URL"
        return 1
    fi
}

# Función para configurar Redis
setup_redis() {
    echo ""
    echo "🔴 Configurando Redis..."

    # Verificar si Redis ya existe
    if heroku addons --app $APP_NAME | grep -q "heroku-redis"; then
        echo "✅ Redis ya está configurado"

        # Obtener información de Redis
        echo "📊 Información de Redis:"
        heroku redis:info --app $APP_NAME
    else
        echo "📦 Instalando Redis..."

        # Instalar Redis (plan básico gratuito)
        if heroku addons:create heroku-redis:mini --app $APP_NAME; then
            echo "✅ Redis instalado exitosamente"
        else
            echo "⚠️ Intentando con plan hobby-dev..."
            heroku addons:create heroku-redis:hobby-dev --app $APP_NAME
        fi
    fi

    # Obtener REDIS_URL
    REDIS_URL=$(heroku config:get REDIS_URL --app $APP_NAME)
    if [ -n "$REDIS_URL" ]; then
        echo "✅ REDIS_URL configurada"
        echo "🔗 URL: ${REDIS_URL:0:30}..."
    else
        echo "❌ No se pudo obtener REDIS_URL"
        return 1
    fi
}

# Función para configurar variables de entorno relacionadas con DB
setup_database_env_vars() {
    echo ""
    echo "⚙️ Configurando variables de entorno de base de datos..."

    heroku config:set \
        DATABASE_CONNECTION_POOL_SIZE=20 \
        DATABASE_CONNECTION_TIMEOUT=30 \
        DATABASE_QUERY_TIMEOUT=60 \
        REDIS_CONNECTION_POOL_SIZE=10 \
        REDIS_CONNECTION_TIMEOUT=10 \
        --app $APP_NAME

    echo "✅ Variables de entorno configuradas"
}

# Función para crear tablas iniciales
setup_initial_tables() {
    echo ""
    echo "🏗️ Configurando estructura inicial de base de datos..."

    # Crear archivo SQL temporal con las tablas iniciales
    cat > /tmp/init_db.sql << 'EOF'
-- Tabla para métricas del sistema
CREATE TABLE IF NOT EXISTS system_metrics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,2),
    metric_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla para logs de API calls
CREATE TABLE IF NOT EXISTS api_logs (
    id SERIAL PRIMARY KEY,
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER,
    response_time_ms INTEGER,
    user_agent TEXT,
    ip_address INET,
    request_data JSONB,
    response_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla para almacenar análisis de AI
CREATE TABLE IF NOT EXISTS ai_analyses (
    id SERIAL PRIMARY KEY,
    analysis_type VARCHAR(50) NOT NULL,
    input_text TEXT NOT NULL,
    analysis_result JSONB NOT NULL,
    model_used VARCHAR(100),
    processing_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla para datos médicos de Panacea
CREATE TABLE IF NOT EXISTS medical_data (
    id SERIAL PRIMARY KEY,
    participant_id VARCHAR(100),
    data_type VARCHAR(50) NOT NULL,
    medical_data JSONB NOT NULL,
    risk_score DECIMAL(5,2),
    panacea_response JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla para tokens PANAS
CREATE TABLE IF NOT EXISTS panas_tokens (
    id SERIAL PRIMARY KEY,
    wallet_address VARCHAR(100) NOT NULL,
    token_amount DECIMAL(20,6) NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,
    transaction_hash VARCHAR(100),
    blockchain_network VARCHAR(20) DEFAULT 'algorand',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crear índices para mejor performance
CREATE INDEX IF NOT EXISTS idx_api_logs_endpoint ON api_logs(endpoint);
CREATE INDEX IF NOT EXISTS idx_api_logs_created_at ON api_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_ai_analyses_type ON ai_analyses(analysis_type);
CREATE INDEX IF NOT EXISTS idx_medical_data_participant ON medical_data(participant_id);
CREATE INDEX IF NOT EXISTS idx_panas_tokens_wallet ON panas_tokens(wallet_address);

-- Insertar datos iniciales de métricas
INSERT INTO system_metrics (metric_name, metric_value, metric_data)
VALUES
    ('total_api_calls', 0, '{"description": "Total API calls made"}'),
    ('active_users', 0, '{"description": "Current active users"}'),
    ('ai_analyses_count', 0, '{"description": "Total AI analyses performed"}'),
    ('medical_records_processed', 0, '{"description": "Medical records processed"}'),
    ('panas_tokens_distributed', 0, '{"description": "Total PANAS tokens distributed"}')
ON CONFLICT DO NOTHING;
EOF

    # Ejecutar SQL en la base de datos de Heroku
    echo "📝 Ejecutando script de inicialización..."
    if heroku pg:psql --app $APP_NAME < /tmp/init_db.sql; then
        echo "✅ Estructura de base de datos creada exitosamente"
    else
        echo "❌ Error al crear estructura de base de datos"
        return 1
    fi

    # Limpiar archivo temporal
    rm -f /tmp/init_db.sql
}

# Función para verificar la configuración
verify_database_setup() {
    echo ""
    echo "🔍 Verificando configuración de base de datos..."

    # Verificar conexión a PostgreSQL
    echo "📊 Verificando PostgreSQL..."
    if heroku pg:psql --app $APP_NAME -c "\dt" > /dev/null 2>&1; then
        echo "✅ Conexión a PostgreSQL exitosa"

        # Mostrar tablas creadas
        echo "📋 Tablas en la base de datos:"
        heroku pg:psql --app $APP_NAME -c "\dt"
    else
        echo "❌ Error de conexión a PostgreSQL"
        return 1
    fi

    # Verificar Redis si está configurado
    if heroku config:get REDIS_URL --app $APP_NAME > /dev/null 2>&1; then
        echo "✅ Redis configurado correctamente"
    fi

    # Mostrar todas las configuraciones
    echo ""
    echo "📋 Variables de entorno relacionadas con base de datos:"
    heroku config --app $APP_NAME | grep -E "(DATABASE|REDIS|DB_)"
}

# Función para mostrar información útil
show_database_info() {
    echo ""
    echo "📚 Información de Base de Datos"
    echo "==============================="
    echo ""
    echo "🔗 Conexiones:"
    echo "  • PostgreSQL: heroku pg:psql --app $APP_NAME"
    echo "  • Redis: heroku redis:cli --app $APP_NAME"
    echo ""
    echo "📊 Monitoreo:"
    echo "  • PostgreSQL stats: heroku pg:info --app $APP_NAME"
    echo "  • Redis stats: heroku redis:info --app $APP_NAME"
    echo ""
    echo "🛠️ Utilidades:"
    echo "  • Backup DB: heroku pg:backups:capture --app $APP_NAME"
    echo "  • Reset DB: heroku pg:reset DATABASE_URL --app $APP_NAME"
    echo "  • Ver logs: heroku logs --tail --app $APP_NAME"
    echo ""
    echo "🔧 Configuración completa:"
    echo "  • App URL: $(heroku apps:info $APP_NAME --json | jq -r '.app.web_url' 2>/dev/null || echo 'N/A')"
    echo "  • Región: $(heroku apps:info $APP_NAME --json | jq -r '.app.region.name' 2>/dev/null || echo 'N/A')"
}

# Ejecutar configuración
main() {
    echo "🚀 Iniciando configuración de base de datos..."

    # Configurar PostgreSQL
    if setup_postgresql; then
        echo "✅ PostgreSQL configurado"
    else
        echo "❌ Error configurando PostgreSQL"
        exit 1
    fi

    # Configurar Redis
    if setup_redis; then
        echo "✅ Redis configurado"
    else
        echo "⚠️ Redis no configurado (no crítico)"
    fi

    # Configurar variables de entorno
    setup_database_env_vars

    # Crear estructura inicial
    if setup_initial_tables; then
        echo "✅ Estructura de DB creada"
    else
        echo "❌ Error creando estructura de DB"
        exit 1
    fi

    # Verificar configuración
    if verify_database_setup; then
        echo "✅ Verificación exitosa"
    else
        echo "❌ Error en verificación"
        exit 1
    fi

    # Mostrar información útil
    show_database_info

    echo ""
    echo "🎉 ¡Configuración de base de datos completada exitosamente!"
    echo ""
    echo "🔄 Próximos pasos:"
    echo "1. Deploy tu aplicación: ./deploy_heroku.sh $APP_NAME"
    echo "2. Verificar que funciona: heroku open --app $APP_NAME"
    echo "3. Monitorear logs: heroku logs --tail --app $APP_NAME"
}

# Ejecutar función principal
main
