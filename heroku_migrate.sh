#!/bin/bash

# Script para ejecutar migraciones después del deploy en Heroku
# Uso: ./heroku_migrate.sh [app-name]

set -e

APP_NAME=${1:-"panas-token-api"}

echo "📊 Ejecutando migraciones en Heroku para: $APP_NAME"
echo "================================================"

# Verificar que la app existe
if ! heroku apps:info $APP_NAME &> /dev/null; then
    echo "❌ La app $APP_NAME no existe en Heroku"
    exit 1
fi

# Verificar que PostgreSQL está configurado
if ! heroku config:get DATABASE_URL --app $APP_NAME > /dev/null; then
    echo "❌ PostgreSQL no está configurado para $APP_NAME"
    echo "💡 Ejecutar primero: ./setup_heroku_database.sh $APP_NAME"
    exit 1
fi

# Crear script de migración temporal
cat > /tmp/migrate.sql << 'EOF'
-- Crear extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tabla para métricas del sistema
CREATE TABLE IF NOT EXISTS system_metrics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100) UNIQUE NOT NULL,
    metric_value DECIMAL(15,2),
    metric_data JSONB DEFAULT '{}',
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
    request_data JSONB DEFAULT '{}',
    response_data JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla para análisis de AI
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
    panacea_response JSONB DEFAULT '{}',
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

-- Tabla para usuarios
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    user_id UUID DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE,
    wallet_address VARCHAR(100),
    user_type VARCHAR(50) DEFAULT 'researcher',
    profile_data JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crear índices para mejor performance
CREATE INDEX IF NOT EXISTS idx_api_logs_endpoint ON api_logs(endpoint);
CREATE INDEX IF NOT EXISTS idx_api_logs_created_at ON api_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_ai_analyses_type ON ai_analyses(analysis_type);
CREATE INDEX IF NOT EXISTS idx_medical_data_participant ON medical_data(participant_id);
CREATE INDEX IF NOT EXISTS idx_panas_tokens_wallet ON panas_tokens(wallet_address);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_wallet ON users(wallet_address);

-- Insertar métricas iniciales
INSERT INTO system_metrics (metric_name, metric_value, metric_data) 
VALUES 
    ('total_api_calls', 0, '{"description": "Total API calls made"}'),
    ('active_users', 0, '{"description": "Current active users"}'),
    ('ai_analyses_count', 0, '{"description": "Total AI analyses performed"}'),
    ('medical_records_processed', 0, '{"description": "Medical records processed"}'),
    ('panas_tokens_distributed', 0, '{"description": "Total PANAS tokens distributed"}'),
    ('database_migrations_run', 1, '{"description": "Number of database migrations executed", "last_migration": "initial_setup"}')
ON CONFLICT (metric_name) DO NOTHING;

-- Función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Crear triggers para updated_at
DROP TRIGGER IF EXISTS update_medical_data_updated_at ON medical_data;
CREATE TRIGGER update_medical_data_updated_at 
    BEFORE UPDATE ON medical_data 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_system_metrics_updated_at ON system_metrics;
CREATE TRIGGER update_system_metrics_updated_at 
    BEFORE UPDATE ON system_metrics 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
EOF

echo "📝 Ejecutando migración en PostgreSQL..."
if heroku pg:psql --app $APP_NAME < /tmp/migrate.sql; then
    echo "✅ Migración ejecutada exitosamente"
else
    echo "❌ Error ejecutando migración"
    exit 1
fi

# Limpiar archivo temporal
rm -f /tmp/migrate.sql

# Verificar que las tablas se crearon
echo ""
echo "🔍 Verificando estructura de base de datos..."
heroku pg:psql --app $APP_NAME -c "\dt"

echo ""
echo "📊 Verificando métricas iniciales..."
heroku pg:psql --app $APP_NAME -c "SELECT metric_name, metric_value FROM system_metrics;"

echo ""
echo "🎉 Migración completada exitosamente!"
echo ""
echo "🔗 Comandos útiles:"
echo "  heroku pg:psql --app $APP_NAME"
echo "  heroku pg:info --app $APP_NAME"
echo "  heroku logs --tail --app $APP_NAME"
