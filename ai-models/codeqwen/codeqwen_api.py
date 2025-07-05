#!/usr/bin/env python3
"""
CodeQwen API Server
Servidor API local para el modelo CodeQwen especializado en generación de código
"""

import os
import asyncio
import torch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import uvicorn
from typing import Optional, Dict, Any
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración del modelo
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/CodeQwen1.5-7B-Chat")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4096"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.1"))
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

app = FastAPI(title="CodeQwen API", version="1.0.0")

# Variables globales para el modelo
tokenizer = None
model = None

class CodeRequest(BaseModel):
    prompt: str
    max_tokens: Optional[int] = MAX_TOKENS
    temperature: Optional[float] = TEMPERATURE
    language: Optional[str] = "python"
    task: Optional[str] = "generate"  # generate, explain, fix, optimize

class CodeResponse(BaseModel):
    generated_code: str
    explanation: Optional[str] = None
    language: str
    tokens_used: int
    model_info: Dict[str, Any]

async def load_model():
    """Cargar el modelo CodeQwen"""
    global tokenizer, model

    try:
        logger.info(f"Cargando modelo: {MODEL_NAME}")

        # Configuración para quantización (para ahorrar memoria)
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4"
        )

        # Cargar tokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            MODEL_NAME,
            trust_remote_code=True,
            cache_dir="/app/cache"
        )

        # Cargar modelo
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            quantization_config=quantization_config,
            device_map="auto",
            trust_remote_code=True,
            torch_dtype=torch.float16,
            cache_dir="/app/cache"
        )

        logger.info(f"Modelo cargado exitosamente en {DEVICE}")
        return True

    except Exception as e:
        logger.error(f"Error cargando modelo: {e}")
        return False

def create_coding_prompt(request: CodeRequest) -> str:
    """Crear prompt específico para tareas de programación"""

    task_prompts = {
        "generate": f"Genera código {request.language} para la siguiente tarea:\n{request.prompt}\n\nCódigo:",
        "explain": f"Explica el siguiente código {request.language}:\n{request.prompt}\n\nExplicación:",
        "fix": f"Corrige los errores en este código {request.language}:\n{request.prompt}\n\nCódigo corregido:",
        "optimize": f"Optimiza este código {request.language}:\n{request.prompt}\n\nCódigo optimizado:",
        "refactor": f"Refactoriza este código {request.language} para mejor legibilidad:\n{request.prompt}\n\nCódigo refactorizado:",
    }

    return task_prompts.get(request.task, task_prompts["generate"])

@app.on_event("startup")
async def startup_event():
    """Cargar modelo al iniciar la aplicación"""
    success = await load_model()
    if not success:
        logger.error("Falló la carga del modelo al iniciar")

@app.get("/")
async def root():
    """Endpoint de salud"""
    return {
        "service": "CodeQwen API",
        "status": "running",
        "model": MODEL_NAME,
        "device": DEVICE,
        "model_loaded": model is not None
    }

@app.get("/health")
async def health():
    """Endpoint de verificación de salud"""
    return {
        "status": "healthy" if model is not None else "unhealthy",
        "model_loaded": model is not None,
        "device": DEVICE,
        "gpu_available": torch.cuda.is_available(),
        "gpu_count": torch.cuda.device_count() if torch.cuda.is_available() else 0
    }

@app.post("/generate", response_model=CodeResponse)
async def generate_code(request: CodeRequest):
    """Generar código usando CodeQwen"""

    if model is None or tokenizer is None:
        raise HTTPException(status_code=503, detail="Modelo no cargado")

    try:
        # Crear prompt
        prompt = create_coding_prompt(request)

        # Tokenizar
        inputs = tokenizer.encode(prompt, return_tensors="pt").to(model.device)

        # Generar
        with torch.no_grad():
            outputs = model.generate(
                inputs,
                max_new_tokens=request.max_tokens,
                temperature=request.temperature,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id
            )

        # Decodificar
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extraer solo la parte generada
        generated_code = generated_text[len(prompt):].strip()

        # Información del modelo
        model_info = {
            "model_name": MODEL_NAME,
            "device": str(model.device),
            "dtype": str(model.dtype),
            "memory_usage": torch.cuda.memory_allocated() if torch.cuda.is_available() else 0
        }

        return CodeResponse(
            generated_code=generated_code,
            explanation=f"Código generado para tarea: {request.task}",
            language=request.language,
            tokens_used=len(outputs[0]),
            model_info=model_info
        )

    except Exception as e:
        logger.error(f"Error generando código: {e}")
        raise HTTPException(status_code=500, detail=f"Error generando código: {str(e)}")

@app.get("/models")
async def list_models():
    """Listar modelos disponibles"""
    return {
        "current_model": MODEL_NAME,
        "available_models": [
            "Qwen/CodeQwen1.5-7B-Chat",
            "Qwen/CodeQwen1.5-7B",
            "microsoft/DialoGPT-medium",
            "codellama/CodeLlama-7b-Python-hf"
        ],
        "model_info": {
            "loaded": model is not None,
            "device": DEVICE,
            "parameters": "7B" if "7B" in MODEL_NAME else "Unknown"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "codeqwen_api:app",
        host="0.0.0.0",
        port=5000,
        reload=False,
        workers=1
    )
