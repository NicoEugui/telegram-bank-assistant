# Asistente NicoBank

El Asistente NicoBank es un bot bancario conversacional que simula servicios financieros típicos a través de una interfaz de lenguaje natural. Fue diseñado como un desafío técnico para demostrar la integración de IA, herramientas estructuradas, flujos de autenticación seguros y despliegue modular con Docker.

Este bot funciona en Telegram y está impulsado por OpenAI + LangChain, con soporte para persistencia en Redis, desarrollo local con Docker y despliegues de producción con GitHub Actions.

## Tabla de Contenidos

- [Características](#características)
- [Arquitectura](#arquitectura)
- [Tecnologías](#tecnologías)
- [Primeros Pasos](#primeros-pasos)
- [Entornos](#entornos)
- [Capacidades de Conversación](#capacidades-de-conversación)
- [Seguridad y Autenticación](#seguridad-y-autenticación)
- [Pruebas](#pruebas)
- [Despliegue](#despliegue)
- [CI/CD](#cicd)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Scripts](#scripts)

## Características

- Asistente bancario de lenguaje natural (en español)
- Soporte para entrada de voz: convierte audios en texto usando Whisper de OpenAI
- Autenticación segura basada en PIN
- Consultas de saldo y transacciones
- Simulación de préstamos con tasas de interés dinámicas y perfiles
- Preguntas frecuentes sobre productos bancarios (tarjetas, ahorros, préstamos)
- Estado persistente con Redis
- Integración de LangChain + OpenAI
- Gestión de configuración basada en entornos
- Preparado para Docker en desarrollo y producción
- Flujo de trabajo CI/CD de GitHub Actions con puerta de despliegue en caso de fallo de pruebas

## Arquitectura

```
Usuario
   │
   ▼
Telegram → Manejador Telegram → Agente LangChain → Llamadas a Herramientas
                                              │
                                              ▼
                                  Redis (auth, balance, préstamos)
```

LangChain maneja la lógica de conversación y el enrutamiento de herramientas.

Redis almacena el estado del usuario: autenticación, saldos, transacciones, préstamos.

Las herramientas son funciones Python expuestas como @tools de LangChain.

## Tecnologías

- Python 3.10
- LangChain
- OpenAI GPT-4o
- FFmpeg para conversión de audios
- Whisper (OpenAI) para transcripción de voz a texto
- Redis (asíncrono + persistencia)
- Docker y Docker Compose
- GitHub Actions (CI/CD)
- API de Bot de Telegram
- Pytest para pruebas

## Primeros Pasos

### Requisitos previos

- Python 3.10+
- Docker y Docker Compose v2+
- Un Token de Bot de Telegram de @BotFather
- Clave API de OpenAI

### Clonar el repositorio

```bash
git clone https://github.com/NicoEugui/telegram-bank-assistant.git
cd telegram-bank-assistant
```

### Configurar variables de entorno

Crea un archivo .env para desarrollo local:

```bash
cp .env.example .env
```

Completa:

```
ENV=development
TELEGRAM_BOT_TOKEN=tu_token_aquí
OPENAI_API_KEY=tu_clave_openai
REDIS_HOST=redis
REDIS_PORT=6379
```

## Entornos

| Modo       | Archivo         | Docker Compose                 | Uso                            |
| ---------- | --------------- | ------------------------------ | ------------------------------ |
| Desarrollo | .env            | docker-compose-development.yml | Desarrollo local en tu máquina |
| Producción | .env.production | docker-compose-production.yml  | Despliegue remoto, CI/CD       |

Todos los entornos se manejan a través de config.py, que valida ENV y carga el archivo .env.\* apropiado.

## Capacidades de Conversación

Ejemplos que el bot entiende:

- "¿Cuánto tengo en mi cuenta?"
- "Mostrame mis últimos movimientos"
- "Necesito un préstamo"
- "¿Cuánto pagaría si pido 100000 en 24 cuotas?"
- "¿Qué tarjetas ofrecen?"
- "¿Dónde están ubicadas las sucursales?"

### Entrada por Voz

Los usuarios pueden enviar audios (formato .ogg desde Telegram). El asistente convierte estos audios en texto usando Whisper (OpenAI) y responde como si hubieran escrito ese mensaje.

Ejemplo:

- (Audio): "¿Cuánto tengo en la cuenta?" → 🧠 Procesado como texto → 💬 "Su saldo actual es de..."

### Ejemplo de Salida de Simulación de Préstamo

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

## Seguridad y Autenticación

La seguridad del usuario es prioritaria en NicoBank. Por ello, ciertas funcionalidades requieren autenticación previa mediante un PIN.

### Flujo de autenticación

- Al inicio de una conversación, el usuario puede interactuar libremente.
- Si intenta acceder a funciones sensibles (consultar saldo, movimientos, historial de préstamos), se le solicitará un PIN.
- Una vez ingresado y validado, se considera autenticado durante un período limitado.

### Funciones que requieren PIN

- `get_balance` – Consulta de saldo
- `get_transactions` – Movimientos recientes
- `get_loan_history` – Historial de préstamos simulados
- `loan_simulator` – (si el perfil requiere autenticación previa)

### PIN por defecto

- El PIN por defecto es `1234`.
- Puede cambiarse modificando la constante `PIN_CODE` dentro del archivo `config.py`.

```python
# config.py
PIN_CODE = "1234"  # Puedes cambiarlo aquí
```

### Almacenamiento y validez

- El estado de autenticación se persiste por usuario en Redis, usando la clave:
`auth_state:{user_id}`
- Cada sesión tiene un TTL (tiempo de expiración) de 1 hora.

### Herramientas utilizadas

`authenticate_user` → Valida el PIN y marca al usuario como autenticado.

`check_authentication` → Verifica si el usuario ya se autenticó previamente.

### Ejemplo de interacción

```
Usuario: Mostrame mis últimos movimientos

Bot: Antes de poder mostrarte esa información, necesito que ingreses tu PIN.

Usuario: 1234

Bot: Autenticación exitosa. Ahora te muestro la información solicitada.
```

## Pruebas

Ejecuta pruebas usando Docker:

```bash
docker-compose -f docker-compose-development.yml up --build
```

Toda la lógica basada en Redis se prueba utilizando fixtures en conftest.py.

Pytest está configurado a través de pytest.ini. Para ejecutar solo un subconjunto:

```bash
docker-compose -f docker-compose-development.yml run --rm app pytest tests/tools/test_get_balance.py
```

## Despliegue

### Desplegar a producción (manualmente)

Asegúrate de estar en la rama main y que tu VM remota esté configurada con:

- Docker y Docker Compose
- Acceso SSH usando tu clave de GitHub Actions

Luego usa el script run_debug.sh:

```bash
./run_debug.sh
```

Este script realizará:

1. Detener y eliminar contenedores, volúmenes y red existentes
2. Construir contenedores sin usar caché
3. Iniciar contenedores en modo desacoplado
4. Mostrar logs en vivo del servicio de la aplicación

O activa el pipeline CI/CD mediante push a main.

## CI/CD

- Utiliza GitHub Actions
- Se activa solo en main
- Ejecuta pruebas primero; despliega solo si las pruebas pasan
- Despliega al servidor remoto mediante SSH (appleboy/ssh-action)
- Obtiene el código más reciente y reinicia los contenedores

Secretos utilizados:

| Nombre       | Descripción           |
| ------------ | --------------------- |
| PROD_HOST    | IP de tu VM           |
| PROD_USER    | Nombre de usuario SSH |
| PROD_SSH_KEY | Clave SSH privada     |

## Estructura del Proyecto

```
.
nicobank/
├── bot/                         # Código fuente del bot
│   ├── agent/                   # Agente conversacional LangChain
│   │   └── conversation_agent.py
│   ├── handlers/                # Manejadores de mensajes de Telegram
│   │   ├── message_handler.py        # Procesa mensajes de texto
│   │   ├── audio_handler.py          # Procesa mensajes de voz (Whisper)
│   │   └── global_error_handler.py   # Manejo global de errores
│   ├── prompts/                 # Prompts base para el agente
│   │   └── system_prompts.py         # Mensajes del sistema (rol IA)
│   ├── services/                # Integraciones y lógica externa
│   │   ├── interaction_tracker.py    # Cuenta interacciones por usuario
│   │   ├── redis_service.py          # Wrapper de Redis para lectura/escritura
│   │   ├── response_humanizer.py     # Mejora la naturalidad de respuestas
│   │   └── whisper_transcriber.py    # Transcripción de voz con OpenAI Whisper
│   ├── tools/                   # Herramientas LangChain (features del banco)
│   │   ├── authenticate_user.py
│   │   ├── check_authentication.py
│   │   ├── get_balance.py
│   │   ├── get_loan_history.py
│   │   ├── get_transactions.py
│   │   └── loan_simulator.py
│   ├── utils/                   # Funciones auxiliares
│   │   ├── audio_converter.py        # Conversión .ogg a .wav con FFmpeg
│   │   └── time_helpers.py           # Formatos y utilidades de tiempo
├── tests/                       # Suite de pruebas unitarias
│   ├── tools/                        # Tests para cada herramienta
│   ├── services/                     # Tests para módulos externos
│   └── conftest.py                  # Fixtures globales de Pytest
├── config.py                    # Carga y validación de entornos
├── main.py                      # Punto de entrada del bot
├── Dockerfile                   # Instrucciones de build Docker
├── docker-compose-development.yml   # Docker Compose para desarrollo
├── docker-compose-production.yml    # Docker Compose para producción
├── run_debug.sh                 # Script para ejecutar el bot en modo debug
├── requirements.txt             # Dependencias Python
├── .env.example                 # Variables de entorno local (ejemplo)
├── .env.production.example      # Variables de entorno producción (ejemplo)
├── .github/
│   └── workflows/
│       └── deploy.yml           # Workflow CI/CD con GitHub Actions
├── README.md                    # Documentación principal
└── .gitignore                   # Exclusiones de Git

```

## Scripts

### run_debug.sh

Este script bash maneja el proceso completo de despliegue:

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

Para usarlo:

1. Haz el script ejecutable: `chmod +x run_debug.sh`
2. Ejecútalo: `./run_debug.sh`
