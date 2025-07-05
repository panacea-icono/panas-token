# 🚀 Guía de Deployment - PANAS Token API

## 📋 Descripción

Esta guía explica cómo desplegar la FastAPI del token PANAS tanto en **Heroku** como en **Docker**, incluyendo la integración con el pipeline de Panacea API Central.

## 🏗️ Arquitectura

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   PANAS Token   │───▶│   FastAPI        │───▶│  Panacea API    │
│   Frontend      │    │   (Heroku/Docker)│    │   Central       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │  Algorand Network│
                       │   + OpenAI       │
                       └──────────────────┘
```

## 🐳 Deployment con Docker

### 1. Desarrollo Local

```bash
# Construir y ejecutar en modo desarrollo
./deploy_docker.sh development

# La API estará disponible en:
# http://localhost:8000
# Documentación: http://localhost:8000/docs
```

### 2. Producción con Docker

```bash
# Ejecutar en modo producción
./deploy_docker.sh production

# La API estará disponible en:
# http://localhost (puerto 80)
```

### 3. Stack Completo con Docker Compose

```bash
# Ejecutar con Redis, PostgreSQL y Nginx
./deploy_docker.sh compose

# Servicios disponibles:
# - API: http://localhost
# - Redis: localhost:6379
# - PostgreSQL: localhost:5432
```

### 4. Comandos Docker Útiles

```bash
# Ver logs
./deploy_docker.sh logs

# Ver estado
./deploy_docker.sh status

# Limpiar todo
./deploy_docker.sh cleanup

# Parar servicios
./deploy_docker.sh stop
```

## ☁️ Deployment en Heroku

### 1. Deployment Automático

```bash
# Desplegar a Heroku con nombre automático
./deploy_heroku.sh

# O especificar nombre de la app
./deploy_heroku.sh mi-panas-api
```

### 2. Deployment Manual

```bash
# 1. Login a Heroku
heroku login

# 2. Crear app
heroku create mi-panas-api

# 3. Configurar variables de entorno
heroku config:set OPENAI_API_KEY=tu_key_aqui
heroku config:set PANACEA_API_URL=https://panacea-central.herokuapp.com

# 4. Agregar add-ons
heroku addons:create heroku-redis:mini
heroku addons:create heroku-postgresql:mini

# 5. Deploy
git push heroku main
```

### 3. Variables de Entorno Requeridas

```bash
# Configurar en Heroku
heroku config:set \
  OPENAI_API_KEY=tu_openai_key \
  PANACEA_API_URL=https://panacea-api-central.herokuapp.com \
  PANACEA_API_KEY=tu_panacea_key \
  ALGORAND_NETWORK=testnet \
  PANAS_TOTAL_SUPPLY=1000000
```

## 🔧 Configuración de Entorno

### Variables Requeridas

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Clave API de OpenAI | `sk-...` |
| `PANACEA_API_URL` | URL de Panacea API Central | `https://panacea-central.herokuapp.com` |
| `PANACEA_API_KEY` | Clave para Panacea API | `panacea_...` |
| `ALGORAND_NETWORK` | Red de Algorand | `testnet` o `mainnet` |
| `PANAS_TOTAL_SUPPLY` | Supply total del token | `1000000` |

### Archivos de Configuración

- `.env` - Desarrollo local
- `.env.production` - Producción
- `Procfile` - Heroku
- `runtime.txt` - Versión de Python para Heroku
- `Dockerfile` - Imagen Docker
- `docker-compose.yml` - Stack completo

## 📚 Endpoints de la API

### 1. Información General

```bash
GET /                 # Info básica de la API
GET /health          # Health check
GET /docs            # Documentación Swagger
```

### 2. Token PANAS

```bash
GET /token/info                    # Información del token
POST /token/simulate-transfer      # Simular transferencia
```

### 3. Integración Panacea

```bash
POST /panacea/analyze-medical      # Análisis médico con IA
POST /panacea/evaluate-risk        # Evaluación de riesgos
POST /panacea/submit-metrics       # Enviar métricas al pipeline
```

### 4. IA Local

```bash
POST /ai/analyze-contract          # Analizar smart contract
POST /ai/generate-prompt          # Generar respuesta IA
```

### 5. Métricas y Admin

```bash
GET /metrics/summary              # Resumen de métricas
POST /admin/sync-panacea         # Sincronizar con Panacea
```

## 🔒 Seguridad

### Headers de Seguridad

- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `X-XSS-Protection: 1; mode=block`

### CORS

Configurado para permitir orígenes específicos en producción.

### Rate Limiting

- 10 requests/segundo por IP
- Burst hasta 20 requests

### Variables Sensibles

Nunca commitear:
- `OPENAI_API_KEY`
- `PANACEA_API_KEY`
- `SECRET_KEY`
- Claves privadas de Algorand

## 📊 Monitoring

### Health Checks

```bash
# Verificar estado de la API
curl https://tu-app.herokuapp.com/health

# Verificar métricas
curl https://tu-app.herokuapp.com/metrics/summary
```

### Logs

```bash
# Heroku
heroku logs --tail --app tu-app

# Docker
docker logs -f panas-api
```

### Métricas Clave

- Tiempo de respuesta de endpoints
- Estado de integración con Panacea
- Número de transacciones simuladas
- Uso de IA (OpenAI/local)

## 🚨 Troubleshooting

### Problemas Comunes

1. **API no inicia**
   ```bash
   # Verificar variables de entorno
   heroku config --app tu-app

   # Verificar logs
   heroku logs --tail --app tu-app
   ```

2. **Error 500 en endpoints**
   ```bash
   # Verificar que las claves API estén configuradas
   curl -H "Content-Type: application/json" \
        -d '{"prompt":"test"}' \
        https://tu-app.herokuapp.com/ai/generate-prompt
   ```

3. **Problemas con Panacea**
   ```bash
   # Verificar conectividad
   curl https://tu-app.herokuapp.com/panacea/analyze-medical
   ```

### Debug Local

```bash
# Modo debug
export DEBUG=true
poetry run python main.py

# Verificar importaciones
poetry run python -c "from main import app; print('OK')"
```

## 🔄 CI/CD

### GitHub Actions

El proyecto incluye workflows para:
- ✅ CI/CD de contratos Algorand
- ✅ CI/CD del frontend
- 🔄 Falta: CI/CD de la FastAPI

### Deployment Automático

Para configurar deployment automático:

1. Configurar secretos en GitHub:
   - `HEROKU_API_KEY`
   - `HEROKU_APP_NAME`
   - `OPENAI_API_KEY`
   - `PANACEA_API_KEY`

2. El workflow deployará automáticamente en push a `main`

## 📈 Escalabilidad

### Heroku

- Usar dynos más grandes: `heroku ps:scale web=1:standard-1x`
- Configurar autoscaling
- Usar Redis para cache
- PostgreSQL para persistencia

### Docker

- Múltiples instancias con load balancer
- Kubernetes para orquestación
- Monitoring con Prometheus/Grafana

## 🌐 Dominios Personalizados

### Heroku

```bash
# Agregar dominio
heroku domains:add tu-dominio.com --app tu-app

# Configurar SSL
heroku certs:auto:enable --app tu-app
```

### Docker

Usar nginx reverse proxy con certificados SSL.

---

## ✅ Checklist de Deployment

### Pre-deployment

- [ ] Variables de entorno configuradas
- [ ] Claves API válidas
- [ ] Tests pasando
- [ ] Documentación actualizada

### Post-deployment

- [ ] Health check funcionando
- [ ] Endpoints respondiendo
- [ ] Integración con Panacea activa
- [ ] Logs sin errores
- [ ] Métricas reportando

### Monitoreo Continuo

- [ ] Uptime monitoring
- [ ] Error tracking (Sentry)
- [ ] Performance monitoring
- [ ] Cost monitoring (Heroku/Cloud)
