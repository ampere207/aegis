#!/usr/bin/env bash
set -euo pipefail

echo "Starting local development stack via Docker Compose"
docker compose -f docker/docker-compose.yml up --build
