#!/usr/bin/env bash
set -euo pipefail

# Start Rasa in the background
rasa run \
  --enable-api \
  --cors "*" \
  --host 0.0.0.0 \
  --port "${RASA_PORT:-5005}" \
  --model "./rasa/models" \
  --endpoints "./rasa/endpoints.yml" \
  --credentials "./rasa/credentials.yml" \
  --data "./rasa/data" \
  --config "./rasa/config.yml" \
  --domain "./rasa/domain.yml" &

# Start Flask (Gunicorn)
exec gunicorn -b 0.0.0.0:"${PORT:-5000}" backend.app:app
