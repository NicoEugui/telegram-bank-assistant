# 🏦 NicoBank - Telegram Banking Assistant

**NicoBank** es un asistente conversacional bancario desarrollado para interactuar en lenguaje natural a través de Telegram, simulando servicios clave de una entidad financiera moderna.

## 🧠 Funcionalidades

- Consulta de preguntas frecuentes bancarias (tarjetas, préstamos, plazos fijos, etc.)
- Respuestas humanizadas con tono cálido y estructura conversacional realista
- Historial de conversación con memoria persistente en Redis
- Preparado para extender a saldo, movimientos, autenticación y préstamos simulados
- Contenedor Docker listo para ejecutar

## 🚀 Cómo ejecutar

### Requisitos

- Docker y Docker Compose

### 1. Cloná el repositorio

```bash
git clone https://github.com/tu-usuario/nicobank.git
cd nicobank
```

### 2. Configurá las variables de entorno

Creá un archivo `.env` en la raíz con el siguiente contenido:

```env
TELEGRAM_BOT_TOKEN=tu_token_de_bot
OPENAI_API_KEY=tu_clave_openai
OPENAI_MODEL=gpt-4
REDIS_HOST=nicobank-redis
REDIS_PORT=6379
SESSION_TTL_SECONDS=200
CONTEXT_WINDOW_LENGTH=5
```

> ⚠️ Reemplazá los valores por los tuyos.

### 3. Levantá el bot

```bash
docker-compose up --build
```

### 4. Interactuá por Telegram

Buscá tu bot en Telegram y comenzá a conversar escribiendo mensajes como:

- `Hola`
- `¿Qué tarjetas ofrecen?`
- `Quiero pedir un préstamo`
- `Quiero abrir una caja de ahorro`

## 📸 Ejemplo de interacción

```
Usuario: hola
Bot: Bienvenido a NicoBank!
Bot: Soy Guillermo, su asistente virtual
Bot: ¿En qué puedo ayudarle hoy?
```

---

## 🧪 Testing

Se puede ejecutar pruebas con `pytest` en el futuro (en construcción).

## 🛠️ Stack técnico

- Python 3.10
- Telegram Bot API (`python-telegram-bot v20`)
- LangChain + OpenAI
- Redis (memoria + sesión)
- Docker / Docker Compose

## 🛡️ Manejo de errores global

Agrege este `error_handler` global para capturar fallos inesperados en producción:

```python
# bot/handlers/global_error_handler.py
from telegram.ext import ContextTypes
from telegram import Update
import logging

logger = logging.getLogger(__name__)

async def global_error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception(f"[Global Error] Unexpected error: {context.error}")
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "Ocurrió un error inesperado. Ya estamos trabajando para solucionarlo."
        )
```

Y registralo en tu `main.py`:

```python
from bot.handlers.global_error_handler import global_error_handler

app.add_error_handler(global_error_handler)
```

---

## ✨ Autor

Desarrollado por Nicolas Eugui