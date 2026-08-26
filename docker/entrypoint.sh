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

if [ "${IMPORT_SQL_ON_START:-true}" = "true" ] && [ -f /app/data/seed.sql ]; then
  echo "Checking database initialization state..."
  mysql_app() {
    MYSQL_PWD="$DB_PASSWORD" mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" "$DB_NAME" -N -B "$@"
  }

  APP_TABLE_COUNT="$(mysql_app -e "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name <> 'app_import_state';")"

  if [ "$APP_TABLE_COUNT" = "0" ]; then
    mysql_app -e "CREATE TABLE IF NOT EXISTS app_import_state (id TINYINT PRIMARY KEY, status VARCHAR(20) NOT NULL, updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP);"

    if mysql_app -e "INSERT INTO app_import_state (id, status) VALUES (1, 'running');"; then
      echo "Database is empty; importing data/seed.sql..."
      if MYSQL_PWD="$DB_PASSWORD" mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" --binary-mode "$DB_NAME" < /app/data/seed.sql; then
        mysql_app -e "UPDATE app_import_state SET status = 'done' WHERE id = 1;"
      else
        mysql_app -e "UPDATE app_import_state SET status = 'failed' WHERE id = 1;" || true
        exit 1
      fi
    else
      echo "Another process is importing initial data; waiting for it to finish..."
      i=0
      while [ "$i" -lt 120 ]; do
        IMPORT_STATUS="$(mysql_app -e "SELECT status FROM app_import_state WHERE id = 1;")"
        if [ "$IMPORT_STATUS" = "done" ]; then
          echo "Initial data import completed by another process."
          break
        elif [ "$IMPORT_STATUS" = "failed" ]; then
          echo "Initial data import failed in another process."
          exit 1
        fi
        sleep 2
        i=$((i + 1))
      done

      if [ "$IMPORT_STATUS" != "done" ]; then
        echo "Timed out waiting for initial data import."
        exit 1
      fi
    fi
  else
    echo "Database already has ${APP_TABLE_COUNT} application tables; skipping SQL import."
  fi
fi

python manage.py collectstatic --noinput
python manage.py migrate --noinput

exec gunicorn food_master.wsgi:application --bind "0.0.0.0:${APP_PORT}" --workers "${GUNICORN_WORKERS:-3}" --timeout "${GUNICORN_TIMEOUT:-120}"
