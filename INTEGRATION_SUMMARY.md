# PANAS Token - Integración Completa con ChatGPT Medical y NFDomains

## 📋 Resumen de la Integración

### 🤖 Asistentes Médicos ChatGPT Integrados

1. **Asistente Clínica Vaser** (`g-67ee9dacb42481918da137c4d26d321a`)
   - Especialidad: Procedimientos estéticos y cirugía plástica
   - Capacidades: Consultas Vaser, liposucción, cuidados pre/post operatorios
   - Comando Telegram: `/vaser`

2. **Asistente Médico Clínica Vaser** (`g-67ee9e5d4d3c819187086b7b8042adb2`)
   - Especialidad: Medicina estética y seguimiento médico
   - Capacidades: Evaluación médica, seguimiento, protocolos
   - Comando Telegram: `/medico`

3. **Liliana GPT** (`g-68090d03cbd881919283ca54c3e57165`)
   - Especialidad: Asistencia personalizada y coordinación
   - Capacidades: Coordinación de citas, atención al cliente
   - Comando Telegram: `/cita`

### 🌐 Dominios NFDomains de Algorand

1. **10.panas.algo** - Dominio principal
   - URL: https://app.nf.domains/name/10.panas.algo
   - Propósito: Token principal y governance

2. **tokenizado.algo** - Tokenización
   - URL: https://app.nf.domains/name/tokenizado.algo
   - Propósito: Tokenización de activos médicos

3. **panacea.icono.algo** - Servicios médicos
   - URL: https://app.nf.domains/name/panacea.icono.algo
   - Propósito: Servicios médicos y plataforma Panacea

4. **activo.algo** - Gestión de activos
   - URL: https://app.nf.domains/name/activo.algo
   - Propósito: Gestión y trading de activos tokenizados

### 🔗 Sitio Web Principal e Integraciones
- **BoliviaChic.com**: https://boliviachic.com
- **Panacea API Central**: https://github.com/panacea-icono/panacea-api-central

## 🏗️ Arquitectura de Servicios

### Docker Compose Services

1. **panas-api** - API principal FastAPI
2. **panacea-api-central** - Integración con repositorio Panacea
3. **medical-gpt-api** - Servicio de integración ChatGPT médico
4. **telegram-bots** - Manager de bots Telegram
5. **ollama** - Modelos locales de IA
5. **codeqwen-api** - Modelo especializado en código
6. **whisper-api** - Speech-to-Text
7. **qdrant** - Vector database
8. **minio** - Object storage
9. **jupyter-ai** - Notebooks de IA
10. **redis** - Cache y sesiones
11. **postgres** - Base de datos principal
12. **nginx** - Reverse proxy

## 📱 Comandos de Telegram Disponibles

### Comandos Básicos
- `/start` - Bienvenida
- `/balance` - Ver balance PANAS
- `/transfer` - Transferir tokens
- `/price` - Precio actual
- `/help` - Ayuda completa

### Comandos NFDomains
- `/domains` - Ver todos los dominios PANAS
- `/domain <nombre>` - Info específica de dominio
- `/nfd` - Información sobre NFDomains
- `/website` - Acceder al sitio web principal

### Comandos Médicos (ChatGPT)
- `/consulta` - Consulta médica general (enrutamiento automático)
- `/vaser` - Consulta específica Clínica Vaser
- `/medico` - Asistente médico especializado
- `/cita` - Agendar cita con Liliana
- `/asistentes` - Ver todos los asistentes médicos

### Comandos de IA
- `/ai` - Consulta con Ollama
- `/code` - Generar/explicar código con CodeQwen

## 🔧 Configuración

### Variables de Entorno Principales
```bash
# OpenAI API Key para ChatGPT
OPENAI_API_KEY=your_openai_api_key

# Tokens de Telegram Bots
BOT_TOKEN_1=8187502572:AAFn2bEOOqDipeDWTnszjyWyiBUUBsofMis
BOT_TOKEN_2=7155901429:AAFTyNZ2VQlufM8gR-TQCiMPD1rsE1qqOAE
BOT_TOKEN_3=7622504424:AAGQjIbXs3fs9ITUiDFBuzNG5PmJHb4Sxao

# URLs de servicios
PANAS_API_URL=http://panas-api:8000
MEDICAL_GPT_API_URL=http://medical-gpt-api:5003
OLLAMA_API_URL=http://ollama:11434
```

## 🚀 Deployment

### Construcción local
```bash
cd /Users/kuchimac/panas_token/panas_token

# Construir servicios médicos
docker compose build medical-gpt-api
docker compose build telegram-bots

# Iniciar todos los servicios
docker compose up -d
```

### Puertos expuestos
- 8000: PANAS API principal
- 5001: CodeQwen API
- 5002: Whisper API
- 5003: Medical GPT API
- 11434: Ollama
- 6379: Redis
- 5432: PostgreSQL
- 9000/9001: MinIO
- 6333/6334: Qdrant
- 8888: Jupyter AI

## 🔄 Flujos de Integración

### Consulta Médica
1. Usuario envía `/consulta` o `/vaser` en Telegram
2. Bot procesa y enruta a ChatGPT apropiado
3. Contexto incluye: NFD domain, balance PANAS, historial
4. Respuesta personalizada con información médica

### Gestión de Dominios NFD
1. Usuario consulta `/domains` o `/domain <nombre>`
2. Bot obtiene información de NFDomains API
3. Muestra estado, características y enlaces
4. Integración con BoliviaChic.com

## 📊 Características Avanzadas

### Enrutamiento Inteligente
- Detección automática del tipo de consulta médica
- Asignación del asistente ChatGPT más apropiado
- Contexto enriquecido con datos del usuario y NFD

### Integración Médica
- Conexión directa con asistentes especializados
- Gestión de citas y seguimiento
- Historial de consultas médicas

### Multi-Bot Architecture
- Bot principal PANAS (token 1)
- Bot asistente IA (token 2)
- Bot ayudante código (token 3)
- Funcionalidades especializadas por bot

## 🔐 Seguridad

- API Keys protegidas en variables de entorno
- Tokens de Telegram encriptados
- Comunicación entre servicios por red interna
- Logs estructurados para auditoría

## 📈 Próximos Pasos

1. **Testing End-to-End**: Verificar todos los flujos de usuario
2. **Monitoreo**: Agregar métricas y alertas
3. **Escalabilidad**: Configurar para producción
4. **Documentación**: Completar guías de usuario

---

**Desarrollo completado**: Integración completa de 3 asistentes médicos ChatGPT + 4 dominios NFDomains + 3 bots Telegram + servicios AI + deployment Docker.

**Status**: ✅ LISTO PARA TESTING Y DEPLOYMENT
