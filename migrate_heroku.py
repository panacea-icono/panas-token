#!/usr/bin/env python3
"""
Script para ejecutar migraciones en Heroku sin dependencias externas
"""

import os
import asyncio
import asyncpg
import sys

async def create_tables():
    """Crear las tablas principales del sistema"""

    # Obtener URL de la base de datos desde variables de entorno
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL no está configurada")
        return False
    
    # Corregir el esquema de URL para asyncpg
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    try:
        # Conectar a la base de datos
        conn = await asyncpg.connect(database_url)
        print("✅ Conectado a PostgreSQL")

        # Crear tabla system_metrics
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS system_metrics (
                id SERIAL PRIMARY KEY,
                metric_name VARCHAR(100) NOT NULL,
                metric_value NUMERIC NOT NULL,
                metric_type VARCHAR(50) NOT NULL,
                metadata JSONB,
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ Tabla system_metrics creada")

        # Crear tabla api_logs
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS api_logs (
                id SERIAL PRIMARY KEY,
                endpoint VARCHAR(255) NOT NULL,
                method VARCHAR(10) NOT NULL,
                status_code INTEGER NOT NULL,
                response_time NUMERIC,
                ip_address INET,
                user_agent TEXT,
                request_data JSONB,
                response_data JSONB,
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ Tabla api_logs creada")

        # Crear tabla ai_analyses
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS ai_analyses (
                id SERIAL PRIMARY KEY,
                analysis_type VARCHAR(100) NOT NULL,
                input_data JSONB NOT NULL,
                output_data JSONB,
                model_used VARCHAR(100),
                confidence_score NUMERIC,
                processing_time NUMERIC,
                status VARCHAR(50) DEFAULT 'completed',
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ Tabla ai_analyses creada")

        # Crear tabla medical_data
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS medical_data (
                id SERIAL PRIMARY KEY,
                patient_id VARCHAR(100),
                data_type VARCHAR(100) NOT NULL,
                encrypted_data BYTEA,
                metadata JSONB,
                access_level VARCHAR(50) DEFAULT 'restricted',
                last_accessed TIMESTAMP WITH TIME ZONE,
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ Tabla medical_data creada")

        # Crear tabla panas_tokens
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS panas_tokens (
                id SERIAL PRIMARY KEY,
                transaction_id VARCHAR(255) UNIQUE NOT NULL,
                from_address VARCHAR(255),
                to_address VARCHAR(255),
                amount NUMERIC NOT NULL,
                token_type VARCHAR(50) DEFAULT 'PANAS',
                transaction_hash VARCHAR(255),
                block_number BIGINT,
                status VARCHAR(50) DEFAULT 'pending',
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ Tabla panas_tokens creada")

        # Crear tabla users
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                role VARCHAR(50) DEFAULT 'user',
                wallet_address VARCHAR(255),
                profile_data JSONB,
                is_active BOOLEAN DEFAULT TRUE,
                last_login TIMESTAMP WITH TIME ZONE,
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ Tabla users creada")

        # Crear índices para optimización
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp ON system_metrics(timestamp);")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_api_logs_timestamp ON api_logs(timestamp);")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_api_logs_endpoint ON api_logs(endpoint);")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_ai_analyses_timestamp ON ai_analyses(timestamp);")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_panas_tokens_transaction_id ON panas_tokens(transaction_id);")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")
        print("✅ Índices creados")

        # Insertar datos de ejemplo
        await conn.execute("""
            INSERT INTO system_metrics (metric_name, metric_value, metric_type, metadata)
            VALUES ('database_setup', 1, 'system', '{"status": "initialized", "version": "1.0"}')
            ON CONFLICT DO NOTHING;
        """)
        print("✅ Datos de ejemplo insertados")

        await conn.close()
        print("✅ Migraciones completadas exitosamente")
        return True

    except Exception as e:
        print(f"❌ Error durante las migraciones: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(create_tables())
    sys.exit(0 if success else 1)
