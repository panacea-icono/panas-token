# Dockerfile para PANAS Token API
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar Poetry
RUN pip install poetry

# Configurar Poetry para no crear entorno virtual (usamos el del contenedor)
ENV POETRY_VENV_IN_PROJECT=false
ENV POETRY_NO_INTERACTION=1
ENV POETRY_CACHE_DIR=/tmp/poetry_cache

# Copiar archivos de configuración de Poetry
COPY pyproject.toml poetry.lock ./

# Instalar dependencias
RUN poetry install --no-dev && rm -rf $POETRY_CACHE_DIR

# Copiar código fuente
COPY . .

# Crear usuario no-root para seguridad
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser:appuser /app
USER appuser

# Exponer puerto
EXPOSE 8000

# Variables de entorno por defecto
ENV HOST=0.0.0.0
ENV PORT=8000
ENV PYTHONPATH=/app

# Comando de inicio
CMD ["poetry", "run", "python", "main.py"]
