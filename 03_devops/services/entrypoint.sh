#!/bin/sh
set -eu

: "${SERVICE_MODULE:?SERVICE_MODULE is required}"
: "${SERVICE_PORT:?SERVICE_PORT is required}"

DB_HOST="${SERVICE_DB_HOST:-db}"
DB_PORT="${SERVICE_DB_PORT:-3306}"
SETTINGS_MODULE="services.${SERVICE_MODULE}.config.settings"

echo "Waiting for database at ${DB_HOST}:${DB_PORT}..."
until nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 2
done

attempt=1
until python -m django migrate --noinput --settings="$SETTINGS_MODULE"; do
  if [ "$attempt" -ge 30 ]; then
    echo "Database migration failed after ${attempt} attempts." >&2
    exit 1
  fi
  attempt=$((attempt + 1))
  sleep 2
done

exec gunicorn "services.${SERVICE_MODULE}.config.wsgi:application" \
  --bind "0.0.0.0:${SERVICE_PORT}" \
  --workers "${GUNICORN_WORKERS:-2}" \
  --timeout "${GUNICORN_TIMEOUT:-60}"
