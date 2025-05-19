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
- [Scripts](#scripts)

## Features

- Natural language banking assistant (in Spanish)
- Voice input support: converts audio to text using OpenAI Whisper
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
- FFmpeg for audio conversion
- Whisper (OpenAI) for voice-to-text transcription
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

| Mode        | File            | Docker Compose                 | Use                               |
| ----------- | --------------- | ------------------------------ | --------------------------------- |
| Development | .env            | docker-compose-development.yml | Local development on your machine |
| Production  | .env.production | docker-compose-production.yml  | Remote deploy to VM, CI/CD        |

All environments are handled via config.py, which validates ENV and loads the appropriate .env.\* file.

## Conversation Capabilities

Examples the bot understands:

- "¿Cuánto tengo en mi cuenta?"
- "Mostrame mis últimos movimientos"
- "Necesito un préstamo"
- "¿Cuánto pagaría si pido 100000 en 24 cuotas?"
- "¿Qué tarjetas ofrecen?"
- "¿Dónde están ubicadas las sucursales?"

### Voice Input

Users can send voice messages (OGG format from Telegram). The assistant converts these audio files into text using Whisper (OpenAI) and replies as if the user had typed that message.

Example:

- (Audio): "How much money do I have?" → 🧠 Processed as text → 💬 "Your current balance is..."

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

Run tests using Docker:

```bash
docker-compose -f docker-compose-development.yml up --build
```

All Redis-based logic is tested using fixtures in conftest.py.

Pytest is configured via pytest.ini. To run only a subset:

```bash
docker-compose -f docker-compose-development.yml run --rm app pytest tests/tools/test_get_balance.py
```

## Deployment

### Deploy to production (manually)

Ensure you're on main branch and your remote VM is set up with:

- Docker & Docker Compose
- SSH access using your GitHub Actions key

Then use the run_debug.sh script:

```bash
./run_debug.sh
```

This script will:

1. Stop and remove existing containers, volumes, and network
2. Build containers without using cache
3. Start containers in detached mode
4. Display live logs from the app service

Or trigger the CI/CD pipeline via push to main.

## CI/CD

- Uses GitHub Actions
- Triggered only on main
- Runs tests first; deploys only if tests pass
- Deploys to remote server via SSH (appleboy/ssh-action)
- Pulls latest code and restarts containers

Secrets used:

| Name         | Description     |
| ------------ | --------------- |
| PROD_HOST    | IP of your VM   |
| PROD_USER    | SSH username    |
| PROD_SSH_KEY | Private SSH key |

## Project Structure

```
.
nicobank/
├── bot/                         # Bot source code
│   ├── agent/                   # LangChain conversational agent
│   │   └── conversation_agent.py
│   ├── handlers/                # Telegram message handlers
│   │   ├── message_handler.py        # Handles text input
│   │   ├── audio_handler.py          # Converts voice messages to text
│   │   └── global_error_handler.py   # Logs and handles unexpected exceptions
│   ├── services/                # External service integrations
│   │   ├── whisper_transcriber.py    # OpenAI Whisper integration
│   │   └── telegram_api.py           # Telegram API helpers (file download, etc.)
│   ├── tools/                   # LangChain tools (banking features)
│   │   ├── authenticate_user.py
│   │   ├── check_authentication.py
│   │   ├── get_balance.py
│   │   ├── get_loan_history.py
│   │   ├── get_transactions.py
│   │   ├── loan_simulator.py
│   ├── utils/                   # Utility functions
│   │   ├── audio_converter.py        # Converts .ogg to .wav using FFmpeg
│   │   └── redis_utils.py            # Redis read/write abstraction
├── tests/                       # Unit test suite
│   ├── tools/                        # Tests for each LangChain tool
│   ├── services/                     # Tests for service modules
│   └── conftest.py                  # Global fixtures for Pytest
├── config.py                    # Loads and validates environment settings
├── main.py                      # Bot entrypoint for Telegram polling
├── Dockerfile                   # Build instructions for Docker image
├── docker-compose-development.yml   # Docker Compose config for development
├── docker-compose-production.yml    # Docker Compose config for production
├── run_debug.sh                 # Shell script to rebuild and run app in prod
├── requirements.txt             # Python dependencies
├── .env.example                 # Local environment template
├── .env.production.example      # Production environment template
├── .github/
│   └── workflows/
│       └── deploy.yml           # GitHub Actions workflow (CI/CD)
├── README.md                    # Main project documentation
└── .gitignore                   # Git exclusions

```

## Scripts

### run_debug.sh

This bash script handles the complete deployment process:

```bash
#!/bin/bash

set -euo pipefail

COMPOSE_FILE="docker-compose-production.yml"
APP_SERVICE="nicobank"

echo "[⚙️] Stopping and removing containers, volumes and network..."
docker-compose -f "$COMPOSE_FILE" down --volumes

echo "[🔧] Building containers without cache..."
docker-compose -f "$COMPOSE_FILE" build --no-cache

echo "[🚀] Starting containers in detached mode..."
docker-compose -f "$COMPOSE_FILE" up -d

echo "[📜] Waiting a few seconds for containers to initialize..."
sleep 3

echo "[🔍] Showing live logs from app service: $APP_SERVICE"
docker-compose -f "$COMPOSE_FILE" logs -f "$APP_SERVICE"
```

To use it:

1. Make the script executable: `chmod +x run_debug.sh`
2. Run it: `./run_debug.sh`
