# NicoBank Assistant

NicoBank Assistant is a conversational banking bot that simulates typical financial services through a natural language interface. It was designed as a technical challenge to demonstrate the integration of AI, structured tools, secure authentication flows, and modular deployment with Docker.

This bot runs on Telegram and is powered by OpenAI + LangChain, with support for Redis persistence, local development with Docker, and GitHub Actions for production deployments.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Technologies](#technologies)
- [Getting Started](#getting-started)
- [Environments](#environments)
- [Conversation Capabilities](#conversation-capabilities)
- [Security and Authentication](#security-and-authentication)
- [Testing](#testing)
- [Deployment](#deployment)
- [CI/CD](#cicd)
- [Project Structure](#project-structure)
- [Makefile Commands](#makefile-commands)

## Features

- Natural language banking assistant (in Spanish)
- Secure PIN-based authentication
- Balance and transaction queries
- Loan simulation with dynamic interest rates and profiles
- FAQ on bank products (cards, savings, loans)
- Persistent state with Redis
- LangChain + OpenAI integration
- Environment-based configuration management
- Docker-ready for dev and prod
- GitHub Actions CI/CD workflow with deploy gate on test failure

## Architecture

```
User
 │
 ▼
Telegram → Telegram Handler → LangChain Agent → Tool Calls
                                          │
                                          ▼
                              Redis (auth, balance, loans)
```

LangChain handles the conversation logic and tool routing.

Redis stores user state: authentication, balances, transactions, loans.

Tools are Python functions exposed as LangChain @tools.

## Technologies

- Python 3.10
- LangChain
- OpenAI GPT-4o
- Redis (async + persistence)
- Docker & Docker Compose
- GitHub Actions (CI/CD)
- Telegram Bot API
- Pytest for testing

## Getting Started

### Prerequisites

- Python 3.10+
- Docker and Docker Compose v2+
- A Telegram Bot Token from @BotFather
- OpenAI API key

### Clone the repository

```bash
git clone https://github.com/NicoEugui/telegram-bank-assistant.git
cd telegram-bank-assistant
```

### Configure environment variables

Create a .env file for local development:

```bash
cp .env.example .env
```

Fill in:

```
ENV=development
TELEGRAM_BOT_TOKEN=your_token_here
OPENAI_API_KEY=your_openai_key
REDIS_HOST=redis
REDIS_PORT=6379
```

## Environments

| Mode | File | Docker Compose | Use |
|------|------|----------------|-----|
| Development | .env | docker-compose-development.yml | Local development on your machine |
| Production | .env.production | docker-compose-production.yml | Remote deploy to GCP, CI/CD |

All environments are handled via config.py, which validates ENV and loads the appropriate .env.* file.

## Conversation Capabilities

Examples the bot understands:

- "¿Cuánto tengo en mi cuenta?"
- "Mostrame mis últimos movimientos"
- "Necesito un préstamo"
- "¿Cuánto pagaría si pido 100000 en 24 cuotas?"
- "¿Qué tarjetas ofrecen?"
- "¿Dónde están ubicadas las sucursales?"

### Loan Simulation Output Example

```
💰 Monto solicitado: 100000 pesos uruguayos
📆 Plazo en cuotas: 24 meses
📟 Cuota estimada: 5333.33 pesos uruguayos
🔢 Total a pagar: 127999.92 pesos uruguayos
💸 Intereses generados: 27999.92 pesos uruguayos
📅 Fecha de simulación: 2025-05-19

Resumen de perfil:
Cliente de riesgo bajo con ingresos mensuales estimados en $45,000 y nivel crediticio 'medium'
```

## Security and Authentication

- Users are required to enter a valid PIN before accessing sensitive features.
- `check_authentication` and `authenticate_user` tools verify and persist session state.
- Each user's state is stored in Redis with a TTL of 1 hour.

## Testing

Run tests locally with:

```bash
make test
```

All Redis-based logic is tested using fixtures in conftest.py.

Pytest is configured via pytest.ini. To run only a subset:

```bash
pytest tests/tools/test_get_balance.py
```

## Deployment

### Deploy to production (manually)

Ensure you're on main branch and your GCP VM is set up with:

- Docker & Docker Compose
- SSH access using your GitHub Actions key

Then:

```bash
make prod
```

Or trigger the CI/CD pipeline via push to main.

## CI/CD

- Uses GitHub Actions
- Triggered only on main
- Runs tests first; deploys only if tests pass
- Deploys to remote server via SSH (appleboy/ssh-action)
- Pulls latest code and restarts containers

Secrets used:

| Name | Description |
|------|-------------|
| PROD_HOST | IP of your VM |
| PROD_USER | SSH username |
| PROD_SSH_KEY | Private SSH key |

## Project Structure

```
.
├── bot/                    # Main agent logic, tools and handlers
├── tests/                  # Pytest-based test suite
├── config.py               # Environment management and validation
├── main.py                 # Bot entrypoint
├── Dockerfile              # Docker build definition
├── Makefile                # CLI shortcuts for dev/prod
├── docker-compose-development.yml
├── docker-compose-production.yml
├── .env.example
├── .env.production.example
├── .github/workflows/     # GitHub Actions CI/CD
```

## Makefile Commands

```
make dev          # Start local development environment
make test         # Run test suite
make logs         # Tail logs from Docker containers
make clean        # Clean containers and volumes
make prod         # Start production build locally (if needed)
```