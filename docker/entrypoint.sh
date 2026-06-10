#!/bin/sh
set -e

DB_HOST="${FOOD_DELIVER_DB_HOST:-${MYSQLHOST:-db}}"
DB_PORT="${FOOD_DELIVER_DB_PORT:-${MYSQLPORT:-3306}}"
DB_NAME="${FOOD_DELIVER_DB_NAME:-${MYSQLDATABASE:-the_food_mas2}}"
DB_USER="${FOOD_DELIVER_DB_USER:-${MYSQLUSER:-root}}"
DB_PASSWORD="${FOOD_DELIVER_DB_PASSWORD:-${MYSQLPASSWORD:-}}"
APP_PORT="${PORT:-8000}"

echo "Waiting for MySQL at ${DB_HOST}:${DB_PORT}..."
until nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 2
done

if [ "${IMPORT_SQL_ON_START:-true}" = "true" ] && [ -f /app/data_hex2.sql ]; then
  TABLE_EXISTS="$(MYSQL_PWD="$DB_PASSWORD" mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" "$DB_NAME" -N -e "SHOW TABLES LIKE 'django_migrations';" || true)"
  if [ -z "$TABLE_EXISTS" ]; then
    echo "Database appears empty; importing data_hex2.sql..."
    MYSQL_PWD="$DB_PASSWORD" mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" --binary-mode "$DB_NAME" < /app/data_hex2.sql
  fi
fi

python manage.py collectstatic --noinput
python manage.py migrate --noinput

exec gunicorn food_master.wsgi:application --bind "0.0.0.0:${APP_PORT}" --workers "${GUNICORN_WORKERS:-3}" --timeout "${GUNICORN_TIMEOUT:-120}"
