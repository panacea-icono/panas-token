FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instalar transformers y dependencias específicas
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
RUN pip install transformers accelerate bitsandbytes

# Copiar código de la aplicación
COPY . .

# Crear directorios necesarios
RUN mkdir -p /app/models /app/cache

# Exponer puerto
EXPOSE 5000

# Variables de entorno
ENV PYTHONPATH=/app
ENV MODEL_CACHE_DIR=/app/cache
ENV TRANSFORMERS_CACHE=/app/cache

# Comando de inicio
CMD ["python", "codeqwen_api.py"]
