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

User security is a priority in NicoBank. Therefore, certain functionalities require prior authentication using a PIN.

### Authentication flow

- At the beginning of a conversation, the user can interact freely.
- If they try to access sensitive features (such as checking balance, transactions, or loan history), a PIN will be requested.
- Once the PIN is entered and validated, the user is considered authenticated for a limited time.

### Features that require PIN

- `get_balance` – Balance inquiry
- `get_transactions` – Recent transactions
- `get_loan_history` – Simulated loan history
- `loan_simulator` – (if the profile requires prior authentication)

### Default PIN

- The default PIN is `1234`.
- You can change it by modifying the `PIN_CODE` constant inside the `config.py` file.

```python
# config.py
PIN_CODE = "1234"  # You can change it here
```

### Storage and validity

- The authentication state is stored per user in Redis, using the key: `auth_state:{user_id}`
- Cada sesión tiene un TTL (tiempo de expiración) de 1 hora.

### Tools used

`authenticate_user` → Validates the PIN and marks the user as authenticated.

`check_authentication` → Verifies whether the user has already authenticated.

### Interaction example

```
User: Show me my latest transactions

Bot: Before I can show you that information, I need you to enter your PIN.

User: 1234

Bot: Authentication successful. Now I’ll show you the requested information.

```

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
│   ├── agent/                   # LangChain conversational agent logic
│   │   └── conversation_agent.py
│   ├── handlers/                # Telegram update handlers
│   │   ├── message_handler.py        # Processes user text messages
│   │   ├── audio_handler.py          # Handles voice input via Whisper
│   │   └── global_error_handler.py   # Captures and logs unexpected exceptions
│   ├── prompts/                 # Prompt engineering definitions
│   │   └── system_prompts.py         # Static system prompts for AI behavior
│   ├── services/                # External service wrappers
│   │   ├── interaction_tracker.py    # Tracks user message count
│   │   ├── redis_service.py          # Redis read/write abstraction
│   │   ├── response_humanizer.py     # Refines assistant replies
│   │   └── whisper_transcriber.py    # Voice-to-text via OpenAI Whisper
│   ├── tools/                   # LangChain tools for banking features
│   │   ├── authenticate_user.py
│   │   ├── check_authentication.py
│   │   ├── get_balance.py
│   │   ├── get_loan_history.py
│   │   ├── get_transactions.py
│   │   └── loan_simulator.py
│   ├── utils/                   # General-purpose utility functions
│   │   ├── audio_converter.py        # Converts Telegram .ogg to .wav with FFmpeg
│   │   └── time_helpers.py           # Formats timestamps and dates
├── tests/                       # Pytest-based unit test suite
│   ├── tools/                        # Tests for LangChain tools
│   ├── services/                     # Tests for service modules
│   └── conftest.py                  # Pytest shared test fixtures
├── config.py                    # Loads environment variables and validates settings
├── main.py                      # Application entrypoint (Telegram polling)
├── Dockerfile                   # Docker image definition
├── docker-compose-development.yml   # Compose config for local development
├── docker-compose-production.yml    # Compose config for remote deployment
├── run_debug.sh                 # Shell script for clean build and live logs
├── requirements.txt             # Python dependency list
├── .env.example                 # Example environment variables for development
├── .env.production.example      # Example environment file for production
├── .github/
│   └── workflows/
│       └── deploy.yml           # GitHub Actions CI/CD pipeline
├── README.md                    # Project overview and instructions
└── .gitignore                   # Files and paths excluded from Git

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
