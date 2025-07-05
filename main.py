"""
FastAPI Server para PANAS Token con integración Panacea

Esta aplicación FastAPI proporciona endpoints para el token PANAS
y se integra con el pipeline de Panacea API Central.
"""

import os
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from openai_integration import AIService
from panacea_integration import PanaceaIntegrationService

# Configuración de la aplicación
app = FastAPI(
    title="PANAS Token API",
    description="API para el token PANAS con integración médica Panacea",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios exactos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servicios globales
panacea_service = PanaceaIntegrationService()
ai_service = AIService()

# Modelos Pydantic


class TokenMetrics(BaseModel):
    transaction_count: int
    active_users: int
    research_projects: int
    total_rewards_distributed: int
    research_categories: List[str]
    geographic_distribution: Dict[str, int]


class ParticipantData(BaseModel):
    age: int
    gender: str
    medical_history: List[str]
    medications: List[str]
    research_type: str
    consent_level: str


class MedicalPrompt(BaseModel):
    prompt: str
    context: Optional[str] = "medical_research"


class ContractAnalysis(BaseModel):
    contract_name: str
    functionality: str


class TokenTransfer(BaseModel):
    from_address: str
    to_address: str
    amount: int
    memo: Optional[str] = None


# Endpoints de salud y estado


@app.get("/")
async def root():
    """Endpoint raíz con información básica."""
    return {
        "service": "PANAS Token API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "integrations": ["panacea", "openai", "algorand"],
    }


@app.get("/health")
async def health_check():
    """Verificación de salud de la API y servicios integrados."""
    try:
        # Verificar integración con Panacea
        panacea_status = await panacea_service.get_integration_status()

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "panacea_integration": panacea_status.get("integration_ready", False),
                "ai_service": True,  # Siempre disponible localmente
                "algorand_network": os.getenv("ALGORAND_NETWORK", "testnet"),
            },
            "token_config": panacea_status.get("token_config", {}),
        }
    except Exception as e:
        return {"status": "partial", "error": str(e), "timestamp": datetime.now().isoformat()}


# Endpoints de integración con Panacea


@app.post("/panacea/analyze-medical")
async def analyze_medical_data(data: MedicalPrompt):
    """Analizar datos médicos usando la IA de Panacea."""
    try:
        result = await panacea_service.analyze_medical_data_with_ai(data.prompt)
        return {
            "status": "success",
            "analysis": result,
            "context": data.context,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en análisis médico: {str(e)}")


@app.post("/panacea/evaluate-risk")
async def evaluate_participant_risk(participant: ParticipantData):
    """Evaluar riesgo de participante en investigación médica."""
    try:
        result = await panacea_service.evaluate_research_participant_risk(participant.dict())
        return {
            "status": "success",
            "risk_evaluation": result,
            "participant_id": f"participant_{datetime.now().timestamp()}",
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en evaluación de riesgo: {str(e)}")


@app.post("/panacea/submit-metrics")
async def submit_token_metrics(metrics: TokenMetrics):
    """Enviar métricas del token PANAS al pipeline de Panacea."""
    try:
        metrics_data = metrics.dict()
        metrics_data["timestamp"] = datetime.now().isoformat()

        result = await panacea_service.submit_panas_metrics(metrics_data)
        return {
            "status": "success",
            "submission_result": result,
            "metrics_submitted": metrics_data,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error enviando métricas: {str(e)}")


# Endpoints de IA local


@app.post("/ai/analyze-contract")
async def analyze_smart_contract(analysis_data: ContractAnalysis):
    """Analizar smart contract usando IA local."""
    try:
        description = await ai_service.generate_smart_contract_description(
            analysis_data.contract_name, analysis_data.functionality
        )
        return {
            "status": "success",
            "contract_analysis": description,
            "contract_name": analysis_data.contract_name,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en análisis de contrato: {str(e)}")


@app.post("/ai/generate-prompt")
async def generate_ai_response(prompt_data: MedicalPrompt):
    """Generar respuesta usando IA local."""
    try:
        # Usar el servicio de IA local para generar respuesta
        messages = [
            {
                "role": "system",
                "content": "Eres un asistente especializado en tokens médicos y blockchain.",
            },
            {"role": "user", "content": prompt_data.prompt},
        ]

        if ai_service.ai_provider == "ollama" and ai_service.ollama_enabled:
            response = await ai_service._call_ollama(messages)
        else:
            response = await ai_service._call_openai(messages)

        return {
            "status": "success",
            "response": response,
            "provider": ai_service.ai_provider,
            "model": ai_service.model,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando respuesta IA: {str(e)}")


# Endpoints del token PANAS


@app.get("/token/info")
async def get_token_info():
    """Obtener información del token PANAS."""
    return {
        "token_name": "PANAS",
        "symbol": "PANAS",
        "network": os.getenv("ALGORAND_NETWORK", "testnet"),
        "total_supply": os.getenv("PANAS_TOTAL_SUPPLY", "1000000"),
        "decimals": int(os.getenv("PANAS_DECIMALS", "6")),
        "use_case": "medical_research_incentive",
        "description": "Token de incentivos para investigación médica en blockchain Algorand",
        "features": [
            "Incentivos para participantes en investigación",
            "Integración con IA médica",
            "Análisis de riesgos automatizado",
            "Métricas de investigación",
        ],
    }


@app.post("/token/simulate-transfer")
async def simulate_token_transfer(transfer: TokenTransfer):
    """Simular transferencia de tokens PANAS."""
    # Esta es una simulación - en producción se conectaría con Algorand
    return {
        "status": "simulated",
        "transaction_id": f"txn_{datetime.now().timestamp()}",
        "from_address": transfer.from_address,
        "to_address": transfer.to_address,
        "amount": transfer.amount,
        "memo": transfer.memo,
        "timestamp": datetime.now().isoformat(),
        "network": os.getenv("ALGORAND_NETWORK", "testnet"),
        "note": "Esta es una simulación. En producción se ejecutaría en Algorand.",
    }


# Endpoints de métricas y estadísticas


@app.get("/metrics/summary")
async def get_metrics_summary():
    """Obtener resumen de métricas del sistema."""
    return {
        "system_metrics": {
            "uptime": "running",
            "integrations_active": 2,
            "last_panacea_sync": datetime.now().isoformat(),
            "ai_provider": getattr(ai_service, "ai_provider", "openai"),
            "network": os.getenv("ALGORAND_NETWORK", "testnet"),
        },
        "token_metrics": {
            "simulated_transactions": 1250,
            "active_researchers": 89,
            "research_projects": 5,
            "total_rewards": 50000,
        },
        "integration_status": {
            "panacea_api": "connected",
            "openai_service": "active",
            "algorand_network": "testnet",
        },
    }


# Tareas en segundo plano


async def sync_with_panacea():
    """Sincronizar datos con Panacea en segundo plano."""
    try:
        # Obtener métricas actuales
        current_metrics = {
            "timestamp": datetime.now().isoformat(),
            "transaction_count": 1250,
            "active_users": 89,
            "research_projects": 5,
            "total_rewards_distributed": 50000,
            "research_categories": ["oncology", "rare_diseases", "neurology"],
        }

        await panacea_service.submit_panas_metrics(current_metrics)
        print(f"✅ Sync con Panacea completado: {datetime.now()}")
    except Exception as e:
        print(f"❌ Error en sync con Panacea: {e}")


@app.post("/admin/sync-panacea")
async def trigger_panacea_sync(background_tasks: BackgroundTasks):
    """Trigger manual de sincronización con Panacea."""
    background_tasks.add_task(sync_with_panacea)
    return {
        "status": "sync_initiated",
        "message": "Sincronización con Panacea iniciada en segundo plano",
        "timestamp": datetime.now().isoformat(),
    }


if __name__ == "__main__":
    import uvicorn

    # Configuración desde variables de entorno
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))

    print(f"🚀 Iniciando PANAS Token API en {host}:{port}")
    print(f"📖 Documentación disponible en: http://{host}:{port}/docs")

    uvicorn.run(
        "main:app", host=host, port=port, reload=os.getenv("DEBUG", "false").lower() == "true"
    )
