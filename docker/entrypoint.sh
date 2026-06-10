#!/bin/sh
set -e

DB_HOST="${FOOD_DELIVER_DB_HOST:-db}"
DB_PORT="${FOOD_DELIVER_DB_PORT:-3306}"

echo "Waiting for MySQL at ${DB_HOST}:${DB_PORT}..."
until nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 2
done

python manage.py collectstatic --noinput
python manage.py migrate --noinput

exec gunicorn food_master.wsgi:application --bind 0.0.0.0:8000 --workers "${GUNICORN_WORKERS:-3}" --timeout "${GUNICORN_TIMEOUT:-120}"
