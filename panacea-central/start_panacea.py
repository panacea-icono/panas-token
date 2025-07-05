#!/usr/bin/env python3
"""
Script de inicio para Panacea API Central integrado con PANAS Token
"""

import os
import sys
import asyncio
import uvicorn
from fastapi import FastAPI
from loguru import logger

# Agregar paths
sys.path.append('/app/panacea-repo')
sys.path.append('/app/integration')

# Configuración
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

def create_integrated_app():
    """Crear aplicación FastAPI integrada"""
    app = FastAPI(
        title="Panacea API Central - PANAS Integration",
        description="API Central de Panacea integrada con PANAS Token",
        version="1.0.0"
    )
    
    # Importar y configurar la app original de Panacea
    try:
        from app.main import app as panacea_app
        
        # Montar la app original de Panacea en /panacea
        app.mount("/panacea", panacea_app)
        logger.info("✅ Panacea API original montada en /panacea")
        
    except ImportError as e:
        logger.warning(f"No se pudo importar Panacea app original: {e}")
    
    # Agregar endpoints de integración PANAS
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "service": "Panacea API Central - PANAS Integration",
            "version": "1.0.0",
            "integrations": {
                "panas_token": True,
                "medical_gpt": True,
                "nfd_domains": True,
                "telegram_bots": True
            }
        }
    
    @app.get("/integration/status")
    async def integration_status():
        """Estado de integración con PANAS"""
        try:
            from panacea_integration import panacea_integration
            async with panacea_integration as api:
                status = await api.get_integration_status()
                return status
        except Exception as e:
            return {"error": str(e), "status": "error"}
    
    @app.post("/integration/sync")
    async def sync_with_panas(user_data: dict):
        """Sincronizar datos con PANAS Token"""
        try:
            from panacea_integration import panacea_integration
            async with panacea_integration as api:
                result = await api.sync_user_data(
                    user_data.get("user_id"),
                    user_data
                )
                return result
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @app.post("/medical/consultation/panas")
    async def panas_medical_consultation(consultation_data: dict):
        """Crear consulta médica con integración PANAS"""
        try:
            from panacea_integration import panacea_integration
            async with panacea_integration as api:
                result = await api.create_medical_consultation(consultation_data)
                return result
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @app.get("/nfd/domains")
    async def get_nfd_domains():
        """Obtener dominios NFD integrados"""
        try:
            domains = {
                "10.panas.algo": {
                    "type": "main",
                    "description": "Dominio principal PANAS Token"
                },
                "tokenizado.algo": {
                    "type": "tokenization", 
                    "description": "Tokenización de activos médicos"
                },
                "panacea.icono.algo": {
                    "type": "medical",
                    "description": "Servicios médicos Panacea"
                },
                "activo.algo": {
                    "type": "assets",
                    "description": "Gestión de activos"
                }
            }
            return {"domains": domains, "total": len(domains)}
        except Exception as e:
            return {"error": str(e)}
    
    logger.info("✅ Aplicación Panacea-PANAS integrada creada")
    return app

async def main():
    """Función principal"""
    logger.info("🏥 Iniciando Panacea API Central - PANAS Integration")
    
    # Crear aplicación integrada
    app = create_integrated_app()
    
    # Configurar servidor
    config = uvicorn.Config(
        app=app,
        host=HOST,
        port=PORT,
        log_level="info",
        access_log=True
    )
    
    server = uvicorn.Server(config)
    
    logger.info(f"🚀 Servidor iniciando en {HOST}:{PORT}")
    logger.info("📋 Endpoints disponibles:")
    logger.info("  - /health - Health check")
    logger.info("  - /integration/status - Estado de integración")
    logger.info("  - /integration/sync - Sincronización con PANAS")
    logger.info("  - /medical/consultation/panas - Consultas médicas")
    logger.info("  - /nfd/domains - Dominios NFD")
    logger.info("  - /panacea/* - API original de Panacea")
    
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
