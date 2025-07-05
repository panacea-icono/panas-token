FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar el repositorio clonado
COPY ./panacea-api-central-repo /app/panacea-repo

# Instalar dependencias Python básicas
RUN pip install --no-cache-dir \
    fastapi>=0.111 \
    uvicorn[standard]>=0.29 \
    openai>=1.30 \
    aiohttp>=3.9.0 \
    redis>=5.0.0 \
    loguru>=0.7.0 \
    pydantic>=2.5.0

# Copiar nuestro código de integración
COPY ./panacea-central /app/integration

# Configurar variables de entorno
ENV PYTHONPATH="/app:/app/panacea-repo:/app/integration"
ENV HOST=0.0.0.0
ENV PORT=8000

# Crear directorio de logs
RUN mkdir -p /app/logs

# Exponer puerto
EXPOSE 8000

# Script de inicio personalizado
COPY ./panacea-central/start_panacea.py /app/start_panacea.py

# Comando de inicio
CMD ["python", "/app/start_panacea.py"]
