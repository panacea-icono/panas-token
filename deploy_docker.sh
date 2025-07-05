#!/bin/bash

# Script de deployment para Docker
# Uso: ./deploy_docker.sh [environment]

set -e

ENVIRONMENT=${1:-development}
IMAGE_NAME="panas-token-api"
CONTAINER_NAME="panas-api"

echo "🐳 Deploying PANAS Token API with Docker"
echo "Environment: $ENVIRONMENT"

# Función para cleanup
cleanup() {
    echo "🧹 Cleaning up..."
    docker stop $CONTAINER_NAME 2>/dev/null || true
    docker rm $CONTAINER_NAME 2>/dev/null || true
}

# Función para build
build_image() {
    echo "🔨 Building Docker image..."
    docker build -t $IMAGE_NAME:latest .
    echo "✅ Image built successfully"
}

# Función para run en development
run_development() {
    echo "🚀 Running in development mode..."

    cleanup

    docker run -d \
        --name $CONTAINER_NAME \
        -p 8000:8000 \
        -v $(pwd):/app \
        --env-file .env \
        -e DEBUG=true \
        -e HOST=0.0.0.0 \
        -e PORT=8000 \
        $IMAGE_NAME:latest

    echo "✅ Container started in development mode"
    echo "🌐 API available at: http://localhost:8000"
    echo "📖 Documentation at: http://localhost:8000/docs"
}

# Función para run en production
run_production() {
    echo "🚀 Running in production mode..."

    cleanup

    docker run -d \
        --name $CONTAINER_NAME \
        -p 80:8000 \
        --env-file .env \
        -e DEBUG=false \
        -e HOST=0.0.0.0 \
        -e PORT=8000 \
        --restart unless-stopped \
        $IMAGE_NAME:latest

    echo "✅ Container started in production mode"
    echo "🌐 API available at: http://localhost"
}

# Función para usar docker-compose
run_compose() {
    echo "🚀 Running with docker-compose..."

    # Detectar versión de docker compose
    if command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    elif docker compose version &> /dev/null; then
        COMPOSE_CMD="docker compose"
    else
        echo "❌ Docker Compose no está disponible"
        exit 1
    fi

    # Parar servicios existentes
    $COMPOSE_CMD down

    # Construir y ejecutar
    $COMPOSE_CMD up --build -d

    echo "✅ Services started with docker-compose"
    echo "🌐 API available at: http://localhost"
    echo "📊 Redis available at: localhost:6379"
    echo "🗄️ PostgreSQL available at: localhost:5432"
}

# Función para mostrar logs
show_logs() {
    echo "📄 Showing container logs..."
    docker logs -f $CONTAINER_NAME
}

# Función para status
show_status() {
    echo "📊 Container status:"
    docker ps --filter name=$CONTAINER_NAME --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

    echo ""
    echo "💾 Image info:"
    docker images $IMAGE_NAME --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
}

# Función para cleanup completo
full_cleanup() {
    echo "🧹 Full cleanup..."

    # Detectar versión de docker compose
    if command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    elif docker compose version &> /dev/null; then
        COMPOSE_CMD="docker compose"
    else
        echo "⚠️ Docker Compose no disponible, solo limpiando containers..."
        cleanup
        docker rmi $IMAGE_NAME:latest 2>/dev/null || true
        echo "✅ Cleanup completed"
        return
    fi

    $COMPOSE_CMD down -v
    cleanup
    docker rmi $IMAGE_NAME:latest 2>/dev/null || true
    echo "✅ Cleanup completed"
}

# Menu principal
case $ENVIRONMENT in
    "development"|"dev")
        build_image
        run_development
        ;;
    "production"|"prod")
        build_image
        run_production
        ;;
    "compose"|"docker-compose")
        run_compose
        ;;
    "logs")
        show_logs
        ;;
    "status")
        show_status
        ;;
    "cleanup")
        full_cleanup
        ;;
    "stop")
        cleanup
        ;;
    *)
        echo "Uso: $0 [development|production|compose|logs|status|cleanup|stop]"
        echo ""
        echo "Comandos disponibles:"
        echo "  development  - Run en modo desarrollo (puerto 8000)"
        echo "  production   - Run en modo producción (puerto 80)"
        echo "  compose      - Run con docker-compose (incluye Redis, PostgreSQL)"
        echo "  logs         - Mostrar logs del container"
        echo "  status       - Mostrar estado del container"
        echo "  cleanup      - Limpiar containers e imágenes"
        echo "  stop         - Parar y remover container"
        exit 1
        ;;
esac

# Mostrar información útil
echo ""
echo "🔧 Comandos útiles:"
echo "  docker logs -f $CONTAINER_NAME"
echo "  docker exec -it $CONTAINER_NAME /bin/bash"
echo "  docker stop $CONTAINER_NAME"
echo "  ./deploy_docker.sh logs"
echo "  ./deploy_docker.sh status"
