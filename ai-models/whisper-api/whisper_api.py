#!/usr/bin/env python3
"""
Whisper API - Speech-to-Text Service
"""

import os
import tempfile
import asyncio
from pathlib import Path
from typing import Optional
import whisper
import torch
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import aiofiles
from loguru import logger

# Configuración
MODEL_SIZE = os.getenv("MODEL_SIZE", "medium")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 5000))

app = FastAPI(title="Whisper API", description="Speech-to-Text Service")

# Cargar modelo Whisper
logger.info(f"Cargando modelo Whisper '{MODEL_SIZE}' en dispositivo: {DEVICE}")
model = whisper.load_model(MODEL_SIZE, device=DEVICE)
logger.info("Modelo Whisper cargado exitosamente")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model": MODEL_SIZE,
        "device": DEVICE,
        "gpu_available": torch.cuda.is_available()
    }

@app.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    language: Optional[str] = None,
    task: str = "transcribe"  # transcribe o translate
):
    """
    Transcribir audio a texto

    Args:
        file: Archivo de audio (mp3, wav, m4a, etc.)
        language: Idioma del audio (opcional, auto-detecta si no se especifica)
        task: 'transcribe' o 'translate' (traducir a inglés)
    """
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser de audio")

    try:
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp_file:
            # Guardar archivo subido
            async with aiofiles.open(temp_file.name, 'wb') as f:
                content = await file.read()
                await f.write(content)

            # Transcribir
            logger.info(f"Transcribiendo archivo: {file.filename}")
            result = model.transcribe(
                temp_file.name,
                language=language,
                task=task,
                verbose=False
            )

            # Limpiar archivo temporal
            os.unlink(temp_file.name)

            response = {
                "text": result["text"],
                "language": result["language"],
                "segments": result["segments"],
                "task": task,
                "model": MODEL_SIZE,
                "device": DEVICE
            }

            logger.info(f"Transcripción completada. Idioma detectado: {result['language']}")
            return JSONResponse(content=response)

    except Exception as e:
        logger.error(f"Error en transcripción: {e}")
        raise HTTPException(status_code=500, detail=f"Error en transcripción: {str(e)}")

@app.post("/detect-language")
async def detect_language(file: UploadFile = File(...)):
    """
    Detectar idioma del audio
    """
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser de audio")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp_file:
            async with aiofiles.open(temp_file.name, 'wb') as f:
                content = await file.read()
                await f.write(content)

            # Detectar idioma (solo los primeros 30 segundos)
            audio = whisper.load_audio(temp_file.name)
            audio = whisper.pad_or_trim(audio)

            # Crear log-Mel spectrogram
            mel = whisper.log_mel_spectrogram(audio).to(model.device)

            # Detectar idioma
            _, probs = model.detect_language(mel)

            os.unlink(temp_file.name)

            # Obtener los top 5 idiomas más probables
            top_languages = sorted(probs.items(), key=lambda x: x[1], reverse=True)[:5]

            return JSONResponse(content={
                "detected_language": max(probs, key=probs.get),
                "confidence": max(probs.values()),
                "top_languages": [{"language": lang, "confidence": conf} for lang, conf in top_languages]
            })

    except Exception as e:
        logger.error(f"Error en detección de idioma: {e}")
        raise HTTPException(status_code=500, detail=f"Error en detección: {str(e)}")

@app.get("/models")
async def list_models():
    """Listar modelos disponibles"""
    return {
        "available_models": ["tiny", "base", "small", "medium", "large"],
        "current_model": MODEL_SIZE,
        "device": DEVICE,
        "supported_languages": list(whisper.tokenizer.LANGUAGES.keys())
    }

if __name__ == "__main__":
    logger.info(f"Iniciando Whisper API en {HOST}:{PORT}")
    uvicorn.run(app, host=HOST, port=PORT)
