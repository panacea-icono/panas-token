# Integración PANAS Token con Panacea API Central

## 🏥 Descripción

Esta integración conecta el token PANAS con la API central de Panacea en Heroku, permitiendo:

- **Análisis médico con IA** especializada en salud
- **Evaluación de riesgos** para participantes en investigación
- **Métricas de token** enviadas al pipeline de análisis central
- **Integración con múltiples APIs** médicas en pipeline

## 🚀 Configuración

### 1. Variables de Entorno

Agrega estas variables a tu archivo `.env`:

```env
# Panacea API Central Integration
PANACEA_API_URL=https://panacea-api-central.herokuapp.com
PANACEA_API_KEY=your_api_key_here

# PANAS Token Configuration
PANAS_TOTAL_SUPPLY=1000000
PANAS_DECIMALS=6
PANAS_TOKEN_NAME=PANAS
PANAS_USE_CASE=medical_research_incentive
```

### 2. URL de la API de Panacea

Basado en el repositorio: `https://github.com/panacea-icono/panacea-api-central`

La API central incluye endpoints para:
- `/chat/` - Análisis con IA médica
- `/sim/risk/` - Simulación de riesgos quirúrgicos
- `/health` - Estado de la API

## 📚 Uso de la Integración

### Ejemplo Básico

```python
from panacea_integration import PanaceaIntegrationService
import asyncio

async def main():
    service = PanaceaIntegrationService()

    # Verificar estado
    status = await service.get_integration_status()
    print(f"Estado: {status}")

    # Análisis médico con IA
    analysis = await service.analyze_medical_data_with_ai(
        "Analiza la viabilidad de incentivos tokenizados para investigación médica"
    )
    print(f"Análisis: {analysis}")

asyncio.run(main())
```

### Evaluación de Riesgo de Participantes

```python
participant_data = {
    "age": 45,
    "gender": "female",
    "medical_history": ["diabetes", "hypertension"],
    "medications": ["metformin", "lisinopril"],
    "research_type": "clinical_trial_phase_2",
    "consent_level": "informed_consent"
}

risk_eval = await service.evaluate_research_participant_risk(participant_data)
```

### Envío de Métricas del Token

```python
metrics = {
    "transaction_count": 1250,
    "active_users": 89,
    "research_projects": 5,
    "total_rewards_distributed": 50000,
    "research_categories": ["oncology", "rare_diseases"]
}

analysis = await service.submit_panas_metrics(metrics)
```

## 🔧 Servicios Disponibles

### 1. PanaceaAPIClient

Cliente base para comunicación con la API:

- `chat_with_ai(prompt)` - Enviar prompts al sistema de IA
- `analyze_surgery_risk(patient_data)` - Análisis de riesgo quirúrgico
- `get_health_status()` - Estado de la API
- `submit_token_analysis(token_data)` - Análisis de métricas de token

### 2. PanaceaIntegrationService

Servicio de integración completo:

- `analyze_medical_data_with_ai()` - Análisis médico especializado
- `evaluate_research_participant_risk()` - Evaluación de participantes
- `submit_panas_metrics()` - Envío de métricas del token
- `get_integration_status()` - Estado de la integración

## 🌐 Arquitectura del Pipeline

La API central de Panacea funciona como un hub que conecta:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   PANAS Token   │───▶│  Panacea API     │───▶│   Multiple      │
│   (Algorand)    │    │   Central        │    │   Medical APIs  │
└─────────────────┘    │   (Heroku)       │    └─────────────────┘
                       └──────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   OpenAI + AI    │
                       │   Medical Models │
                       └──────────────────┘
```

## 📊 Casos de Uso

### 1. Investigación Médica

- **Incentivos tokenizados** para participantes en estudios
- **Análisis de datos** con IA especializada en medicina
- **Gestión de consentimiento** y privacidad

### 2. Evaluación de Riesgos

- **Screening de participantes** para estudios clínicos
- **Análisis de historial médico** automatizado
- **Recomendaciones de elegibilidad**

### 3. Métricas y Analytics

- **Tracking de adoption** del token PANAS
- **Análisis de engagement** en investigación
- **Reportes para stakeholders**

## 🔒 Consideraciones de Seguridad

- **Datos médicos sensibles**: Toda información se maneja según HIPAA/GDPR
- **Autenticación API**: Usar tokens seguros para comunicación
- **Encriptación**: Comunicación HTTPS obligatoria
- **Logs mínimos**: No almacenar datos médicos en logs

## 🚀 Deployment

### Heroku (Recomendado)

```bash
# Configurar variables de entorno en Heroku
heroku config:set PANACEA_API_URL=https://your-panacea-api.herokuapp.com
heroku config:set PANACEA_API_KEY=your_secure_api_key
heroku config:set PANAS_TOTAL_SUPPLY=1000000

# Deploy
git push heroku main
```

### Docker

```dockerfile
# Agregar al Dockerfile
ENV PANACEA_API_URL=https://your-panacea-api.herokuapp.com
ENV PANACEA_API_KEY=your_secure_api_key
```

## 📝 Logging y Monitoring

```python
import logging

# Configurar logging para debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("panacea_integration")

# Monitorear llamadas a la API
service = PanaceaIntegrationService()
status = await service.get_integration_status()
logger.info(f"Panacea API Status: {status}")
```

## 🔧 Troubleshooting

### Errores Comunes

1. **404 Not Found**: Verificar URL de Panacea API en `.env`
2. **Connection Timeout**: Revisar conectividad de red
3. **Auth Errors**: Validar API key de Panacea
4. **Rate Limiting**: Implementar retry logic

### Debug Mode

```python
# Habilitar modo debug
os.environ["DEBUG"] = "true"

# Probar endpoints individuales
python panacea_example.py
```

## 📈 Roadmap

- [ ] **Webhooks** para notificaciones en tiempo real
- [ ] **Batch processing** para análisis masivos
- [ ] **ML model training** con datos de PANAS
- [ ] **Dashboard** para visualización de métricas
- [ ] **API rate limiting** y caching
- [ ] **Multi-language support** para análisis

## 🤝 Contribuir

Para contribuir a la integración:

1. Fork el repositorio
2. Crear branch para feature: `git checkout -b feature/panacea-enhancement`
3. Hacer commit: `git commit -m 'Add Panacea feature'`
4. Push: `git push origin feature/panacea-enhancement`
5. Crear Pull Request

---

**Nota**: Esta integración está diseñada para el ecosistema médico de Panacea. Asegúrate de cumplir con todas las regulaciones médicas y de privacidad aplicables.
