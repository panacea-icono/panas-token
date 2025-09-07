<!-- PANACEA_ECOSYSTEM_HEADER -->
# PANAS-TOKEN

> Parte del ecosistema Panacea | Icono SA. Hub: [Ton-telegram](https://github.com/panacea-icono/Ton-telegram)

- Organización: [@panacea-icono](https://github.com/panacea-icono)
- Documentación de repos: [/docs/REPOSITORIES.md](https://github.com/panacea-icono/Ton-telegram/tree/main/docs/REPOSITORIES.md)
- Estructura y submódulos: [/docs/REPOS-STRUCTURE.md](https://github.com/panacea-icono/Ton-telegram/tree/main/docs/REPOS-STRUCTURE.md)

# panas_token

This starter full stack project has been generated using AlgoKit. See below for default getting started instructions.

## 🆕 Nuevas Dependencias Instaladas

### OpenAI Integration
Este proyecto ahora incluye integración con OpenAI para funcionalidades de IA:

**Backend (Python/Poetry):**

- `openai ^1.93.0` - Cliente oficial de OpenAI para Python
- `python-dotenv ^1.1.1` - Manejo de variables de entorno
- Herramientas de desarrollo: `black`, `ruff`, `mypy`, `pytest`

**Frontend (React/npm):**

- `openai ^5.8.2` - Cliente oficial de OpenAI para JavaScript/TypeScript

### Configuración de OpenAI

1. Copia el archivo `.env.example` a `.env`
2. Agrega tu clave API de OpenAI:
   ```bash
   cp .env.example .env
   # Edita .env y agrega tu OPENAI_API_KEY
   ```

### Uso de OpenAI
Consulta el archivo `openai_integration.py` para ejemplos de:

- Generación de descripciones de smart contracts
- Análisis de código de contratos
- Integración con AlgoKit

## Setup

### Initial setup

1. Clone this repository to your local machine.
2. Ensure [Docker](https://www.docker.com/) is installed and operational. Then, install `AlgoKit` following this [guide](https://github.com/algorandfoundation/algokit-cli#install).
3. Run `algokit project bootstrap all` in the project directory. This command sets up your environment by installing necessary dependencies, setting up a Python virtual environment, and preparing your `.env` file.
4. In the case of a smart contract project, execute `algokit generate env-file -a target_network localnet` from the `panas_token-contracts` directory to create a `.env.localnet` file with default configuration for `localnet`.
5. To build your project, execute `algokit project run build`. This compiles your project and prepares it for running.
6. For project-specific instructions, refer to the READMEs of the child projects:
   - Smart Contracts: [panas_token-contracts](projects/panas_token-contracts/README.md)
   - Frontend Application: [panas_token-frontend](projects/panas_token-frontend/README.md)

> This project is structured as a monorepo, refer to the [documentation](https://github.com/algorandfoundation/algokit-cli/blob/main/docs/features/project/run.md) to learn more about custom command orchestration via `algokit project run`.

### Subsequently

1. If you update to the latest source code and there are new dependencies, you will need to run `algokit project bootstrap all` again.
2. Follow step 3 above.

### Continuous Integration / Continuous Deployment (CI/CD)

This project uses [GitHub Actions](https://docs.github.com/en/actions/learn-github-actions/understanding-github-actions) to define CI/CD workflows, which are located in the [`.github/workflows`](./.github/workflows) folder. You can configure these actions to suit your project's needs, including CI checks, audits, linting, type checking, testing, and deployments to TestNet.

For pushes to `main` branch, after the above checks pass, the following deployment actions are performed:

  - The smart contract(s) are deployed to TestNet using [AlgoNode](https://algonode.io).
  - The frontend application is deployed to a provider of your choice (Netlify, Vercel, etc.). See [frontend README](frontend/README.md) for more information.

> Please note deployment of smart contracts is done via `algokit deploy` command which can be invoked both via CI as seen on this project, or locally. For more information on how to use `algokit deploy` please see [AlgoKit documentation](https://github.com/algorandfoundation/algokit-cli/blob/main/docs/features/deploy.md).

## Tools

This project makes use of Python and React to build Algorand smart contracts and to provide a base project configuration to develop frontends for your Algorand dApps and interactions with smart contracts. The following tools are in use:

- Algorand, AlgoKit, and AlgoKit Utils
- Python dependencies including Poetry, Black, Ruff or Flake8, mypy, pytest, and pip-audit
- React and related dependencies including AlgoKit Utils, Tailwind CSS, daisyUI, use-wallet, npm, jest, playwright, Prettier, ESLint, and Github Actions workflows for build validation

### VS Code

It has also been configured to have a productive dev experience out of the box in [VS Code](https://code.visualstudio.com/), see the [backend .vscode](./backend/.vscode) and [frontend .vscode](./frontend/.vscode) folders for more details.

## Integrating with smart contracts and application clients

Refer to the [panas_token-contracts](projects/panas_token-contracts/README.md) folder for overview of working with smart contracts, [projects/panas_token-frontend](projects/panas_token-frontend/README.md) for overview of the React project and the [projects/panas_token-frontend/contracts](projects/panas_token-frontend/src/contracts/README.md) folder for README on adding new smart contracts from backend as application clients on your frontend. The templates provided in these folders will help you get started.
When you compile and generate smart contract artifacts, your frontend component will automatically generate typescript application clients from smart contract artifacts and move them to `frontend/src/contracts` folder, see [`generate:app-clients` in package.json](projects/panas_token-frontend/package.json). Afterwards, you are free to import and use them in your frontend application.

The frontend starter also provides an example of interactions with your HelloWorldClient in [`AppCalls.tsx`](projects/panas_token-frontend/src/components/AppCalls.tsx) component by default.

## Next Steps

You can take this project and customize it to build your own decentralized applications on Algorand. Make sure to understand how to use AlgoKit and how to write smart contracts for Algorand before you start.

## 🗄️ Configuración de Base de Datos en Heroku

### 📦 Scripts Disponibles

1. **`setup_heroku_database.sh`** - Configuración completa de base de datos
2. **`heroku_migrate.sh`** - Ejecutar migraciones después del deploy
3. **`deploy_heroku.sh`** - Deploy completo con base de datos

### 🚀 Configuración Paso a Paso

#### 1. Configurar Base de Datos
```bash
# Configurar PostgreSQL y Redis en Heroku
./setup_heroku_database.sh [app-name]

# Esto configurará:
# • PostgreSQL (essential-0, mini, o hobby-dev)
# • Redis (mini o hobby-dev)
# • Variables de entorno
# • Estructura inicial de tablas
```

#### 2. Deploy de la Aplicación
```bash
# Deploy con configuración de BD incluida
./deploy_heroku.sh [app-name]

# O deploy paso a paso:
heroku create [app-name]
./setup_heroku_database.sh [app-name]
./deploy_heroku.sh [app-name]
```

#### 3. Ejecutar Migraciones (si es necesario)
```bash
# Ejecutar migraciones adicionales
./heroku_migrate.sh [app-name]
```

### 📊 Estructura de Base de Datos

La aplicación crea automáticamente las siguientes tablas:

```sql
-- Métricas del sistema
system_metrics (id, metric_name, metric_value, metric_data, created_at, updated_at)

-- Logs de API
api_logs (id, endpoint, method, status_code, response_time_ms, user_agent, ip_address, request_data, response_data, created_at)

-- Análisis de AI
ai_analyses (id, analysis_type, input_text, analysis_result, model_used, processing_time_ms, created_at)

-- Datos médicos
medical_data (id, participant_id, data_type, medical_data, risk_score, panacea_response, created_at, updated_at)

-- Tokens PANAS
panas_tokens (id, wallet_address, token_amount, transaction_type, transaction_hash, blockchain_network, created_at)

-- Usuarios
users (id, user_id, email, wallet_address, user_type, profile_data, created_at, updated_at)
```

### 🔗 Endpoints de Base de Datos

La aplicación incluye endpoints para interactuar con la base de datos:

```bash
# Verificar estado de base de datos
GET /database/status

# Obtener métricas de la base de datos
GET /metrics/database

# Actualizar métricas
POST /metrics/update
```

### 🛠️ Comandos Útiles

```bash
# Conectar a PostgreSQL en Heroku
heroku pg:psql --app [app-name]

# Ver información de la base de datos
heroku pg:info --app [app-name]

# Ver logs de la aplicación
heroku logs --tail --app [app-name]

# Backup de la base de datos
heroku pg:backups:capture --app [app-name]

# Reset de la base de datos (¡CUIDADO!)
heroku pg:reset DATABASE_URL --app [app-name]
```

### 📋 Variables de Entorno Automáticas

Heroku configura automáticamente:
- `DATABASE_URL` - URL de conexión a PostgreSQL
- `REDIS_URL` - URL de conexión a Redis

La aplicación detecta automáticamente estas variables y:
- ✅ Usa PostgreSQL en producción (Heroku)
- ✅ Fallback a SQLite en desarrollo local
- ✅ Cache con Redis cuando está disponible
