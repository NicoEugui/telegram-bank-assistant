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
