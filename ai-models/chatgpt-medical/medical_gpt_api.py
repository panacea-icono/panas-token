#!/usr/bin/env python3
"""
Medical GPT API REST Service
Servicio REST para integración con asistentes médicos ChatGPT
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
from loguru import logger

# Importar la integración médica
from medical_gpt_integration import medical_gpt

# Configuración
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 5003))

app = FastAPI(
    title="Medical GPT API",
    description="API REST para integración con asistentes médicos ChatGPT",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class MedicalQuery(BaseModel):
    query: str
    assistant_type: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class AssistantResponse(BaseModel):
    assistant: str
    specialty: str
    response: str
    context: Optional[Dict[str, Any]] = None
    success: bool

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Medical GPT API",
        "version": "1.0.0"
    }

@app.post("/medical/consultation", response_model=AssistantResponse)
async def medical_consultation(query: MedicalQuery):
    """
    Realizar consulta médica con enrutamiento automático
    """
    try:
        response = await medical_gpt.route_medical_query(
            query.query,
            query.context
        )

        if not response["success"]:
            raise HTTPException(status_code=500, detail=response.get("error", "Error en consulta"))

        return AssistantResponse(**response)

    except Exception as e:
        logger.error(f"Error en consulta médica: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/medical/assistant/{assistant_type}", response_model=AssistantResponse)
async def specific_assistant_consultation(assistant_type: str, query: MedicalQuery):
    """
    Consultar con un asistente médico específico

    assistant_type: clinica_vaser, medico_vaser, liliana_gpt
    """
    try:
        response = await medical_gpt.get_assistant_response(
            assistant_type,
            query.query,
            query.context
        )

        if not response["success"]:
            raise HTTPException(status_code=500, detail=response.get("error", "Error en consulta"))

        return AssistantResponse(**response)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error en consulta específica: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/medical/assistants")
async def list_medical_assistants():
    """
    Listar todos los asistentes médicos disponibles
    """
    try:
        return await medical_gpt.get_all_assistants_info()
    except Exception as e:
        logger.error(f"Error listando asistentes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/medical/vaser")
async def vaser_consultation(query: MedicalQuery):
    """
    Consulta específica para Clínica Vaser
    """
    try:
        response = await medical_gpt.get_assistant_response(
            "clinica_vaser",
            query.query,
            query.context
        )

        if not response["success"]:
            raise HTTPException(status_code=500, detail=response.get("error", "Error en consulta Vaser"))

        return AssistantResponse(**response)

    except Exception as e:
        logger.error(f"Error en consulta Vaser: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/medical/appointment")
async def schedule_appointment(query: MedicalQuery):
    """
    Agendar cita con Liliana GPT
    """
    try:
        response = await medical_gpt.get_assistant_response(
            "liliana_gpt",
            query.query,
            query.context
        )

        if not response["success"]:
            raise HTTPException(status_code=500, detail=response.get("error", "Error agendando cita"))

        return AssistantResponse(**response)

    except Exception as e:
        logger.error(f"Error agendando cita: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/medical/doctor")
async def medical_assistant_consultation(query: MedicalQuery):
    """
    Consulta con asistente médico especializado
    """
    try:
        response = await medical_gpt.get_assistant_response(
            "medico_vaser",
            query.query,
            query.context
        )

        if not response["success"]:
            raise HTTPException(status_code=500, detail=response.get("error", "Error en consulta médica"))

        return AssistantResponse(**response)

    except Exception as e:
        logger.error(f"Error en consulta médica: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    logger.info(f"Iniciando Medical GPT API en {HOST}:{PORT}")
    uvicorn.run(app, host=HOST, port=PORT)
