#!/bin/sh
set -e

if [ "$DB_ENGINE" = "mysql" ]; then
    echo "Esperando a que la base de datos ($DB_HOST:$DB_PORT) esté lista..."
    until nc -z "$DB_HOST" "$DB_PORT"; do
        sleep 1
    done
    echo "Base de datos disponible."
fi

python manage.py migrate --noinput
python manage.py collectstatic --noinput --clear || true

exec python manage.py runserver 0.0.0.0:8000
